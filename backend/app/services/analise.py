import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[2] / "noticias_cepea.db"
CORTE = "2026-09-03"
PRACA_POR_MERCADO = {"interno": "parana", "externo": "paranagua"}


def carregar_sentimento(conn, mercado):
    df = pd.read_sql(
        """
        SELECT data, indice_sentimento
        FROM vw_preco_x_sentimento
        WHERE mercado = ? AND data <= ?
        ORDER BY data
        """,
        conn,
        params=(mercado, CORTE),
    )
    df["data"] = pd.to_datetime(df["data"])
    return df


def carregar_var_pct(conn, mercado):
    praca = PRACA_POR_MERCADO[mercado]
    df = pd.read_sql(
        "SELECT data, var_pct FROM precos WHERE praca = ? AND data <= ?",
        conn,
        params=(praca, CORTE),
    )
    df["data"] = pd.to_datetime(df["data"])
    return df.dropna(subset=["var_pct"]).set_index("data")["var_pct"]


def correlacoes_por_defasagem(sentimento, var_pct_por_data, lags=range(6)):
    linhas = []
    for lag in lags:
        datas_futuras = sentimento["data"] + pd.Timedelta(days=lag)
        var_futuro = datas_futuras.map(var_pct_por_data)
        valido = pd.DataFrame({
            "sentimento": sentimento["indice_sentimento"].values,
            "var_pct": var_futuro.values,
        }).dropna()

        if len(valido) < 3:
            continue

        linhas.append({
            "defasagem": lag,
            "pearson": valido["sentimento"].corr(valido["var_pct"]),
            "spearman": valido["sentimento"].rank().corr(valido["var_pct"].rank()),
            "amostras": len(valido),
        })

    return pd.DataFrame(linhas)


def rodar(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    resultados = {}
    for mercado in ("interno", "externo"):
        sentimento = carregar_sentimento(conn, mercado)
        var_pct_por_data = carregar_var_pct(conn, mercado)
        resultados[mercado] = correlacoes_por_defasagem(sentimento, var_pct_por_data)
    conn.close()
    return resultados


if __name__ == "__main__":
    for mercado, tabela in rodar().items():
        print(f"\n{mercado}:")
        print(tabela.to_string(index=False))
