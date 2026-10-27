import sqlite3
from pathlib import Path

import pandas as pd

from app.services.data_loader import carregar_tudo

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "noticias_cepea.db"


def proximo_pregao(data_dia, datas_pregao_ordenadas):
    idx = datas_pregao_ordenadas.searchsorted(data_dia)
    if idx < len(datas_pregao_ordenadas):
        return datas_pregao_ordenadas[idx]
    return None


def montar():
    noticias, precos = carregar_tudo(BASE / "data")

    noticias = noticias.reset_index(drop=True)
    noticias.insert(0, "id", noticias.index + 1)
    noticias["data_dia"] = noticias["data"].dt.date

    precos["data_dia"] = precos["data"].dt.date
    precos = precos.sort_values(["praca", "data_dia"])
    precos["var_pct"] = precos.groupby("praca")["valor_brl"].pct_change() * 100

    datas_pregao = pd.Series(sorted(precos["data_dia"].unique()))
    noticias["data_pregao"] = noticias["data_dia"].apply(lambda d: proximo_pregao(d, datas_pregao))

    noticias["data"] = noticias["data"].astype(str)
    noticias["data_dia"] = noticias["data_dia"].astype(str)
    noticias["data_pregao"] = noticias["data_pregao"].astype(str)

    precos = precos.drop(columns="data_dia")
    precos["data"] = precos["data"].dt.date.astype(str)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    noticias.to_sql("noticias", conn, index=False)
    precos.to_sql("precos", conn, index=False)

    conn.executescript("""
        CREATE TABLE metricas_modelo (
            estrategia TEXT,
            acuracia REAL,
            precisao REAL,
            recall REAL,
            f1 REAL,
            tempo_execucao REAL,
            amostras INTEGER,
            metodo_avaliacao TEXT
        );

        CREATE TABLE metricas_por_classe (
            estrategia TEXT,
            classe TEXT,
            precisao REAL,
            recall REAL,
            f1 REAL,
            suporte INTEGER
        );

        CREATE TABLE resumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periodo TEXT,
            parametros TEXT,
            texto TEXT,
            modelo_llm TEXT,
            gerado_em TEXT
        );

        CREATE INDEX idx_noticias_data_dia ON noticias(data_dia);
        CREATE INDEX idx_noticias_data_pregao ON noticias(data_pregao);
        CREATE INDEX idx_noticias_mercado ON noticias(mercado);
        CREATE INDEX idx_noticias_sentimento ON noticias(sentimento);
        CREATE INDEX idx_precos_data ON precos(data);
        CREATE INDEX idx_precos_praca ON precos(praca);

        CREATE VIEW vw_sentimento_diario AS
        SELECT
            data_pregao AS data,
            mercado,
            SUM(CASE WHEN sentimento = 'positivo' THEN 1 ELSE 0 END) AS qtd_positivo,
            SUM(CASE WHEN sentimento = 'neutro' THEN 1 ELSE 0 END) AS qtd_neutro,
            SUM(CASE WHEN sentimento = 'negativo' THEN 1 ELSE 0 END) AS qtd_negativo,
            COUNT(*) AS qtd_total,
            (SUM(CASE WHEN sentimento = 'positivo' THEN 1 ELSE 0 END) -
             SUM(CASE WHEN sentimento = 'negativo' THEN 1 ELSE 0 END)) * 1.0 / COUNT(*) AS indice_sentimento
        FROM noticias
        WHERE data_pregao IS NOT NULL
        GROUP BY data_pregao, mercado;

        CREATE VIEW vw_sentimento_semanal AS
        SELECT
            strftime('%Y-W%W', data_pregao) AS semana,
            MIN(data_pregao) AS semana_inicio,
            MAX(data_pregao) AS semana_fim,
            mercado,
            SUM(CASE WHEN sentimento = 'positivo' THEN 1 ELSE 0 END) AS qtd_positivo,
            SUM(CASE WHEN sentimento = 'neutro' THEN 1 ELSE 0 END) AS qtd_neutro,
            SUM(CASE WHEN sentimento = 'negativo' THEN 1 ELSE 0 END) AS qtd_negativo,
            COUNT(*) AS qtd_total,
            (SUM(CASE WHEN sentimento = 'positivo' THEN 1 ELSE 0 END) -
             SUM(CASE WHEN sentimento = 'negativo' THEN 1 ELSE 0 END)) * 1.0 / COUNT(*) AS indice_sentimento
        FROM noticias
        WHERE data_pregao IS NOT NULL
        GROUP BY semana, mercado;

        CREATE VIEW vw_preco_x_sentimento AS
        SELECT
            s.data,
            s.mercado,
            CASE s.mercado WHEN 'interno' THEN 'parana' ELSE 'paranagua' END AS praca,
            s.qtd_total,
            s.indice_sentimento,
            p.valor_brl,
            p.valor_usd,
            p.var_pct
        FROM vw_sentimento_diario s
        LEFT JOIN precos p
            ON p.data = s.data
            AND p.praca = CASE s.mercado WHEN 'interno' THEN 'parana' ELSE 'paranagua' END;
    """)

    conn.commit()
    return conn


def testar_integridade(conn):
    erros = []

    total = conn.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    if total != 6320:
        erros.append(f"esperava 6320 noticias, achei {total}")

    for praca in ("parana", "paranagua"):
        qtd = conn.execute("SELECT COUNT(*) FROM precos WHERE praca = ?", (praca,)).fetchone()[0]
        if qtd != 1417:
            erros.append(f"esperava 1417 pregoes em {praca}, achei {qtd}")

    nulos_data = conn.execute("SELECT COUNT(*) FROM noticias WHERE data IS NULL").fetchone()[0]
    if nulos_data:
        erros.append(f"{nulos_data} noticias com data nula")

    sem_pregao = conn.execute("SELECT COUNT(*) FROM noticias WHERE data_pregao IS NULL").fetchone()[0]
    print(f"{sem_pregao} noticias sem pregao correspondente (normal, sao posteriores ao ultimo preco)")

    nulos_preco = conn.execute(
        "SELECT COUNT(*) FROM precos WHERE valor_brl IS NULL OR valor_usd IS NULL"
    ).fetchone()[0]
    if nulos_preco:
        erros.append(f"{nulos_preco} precos nulos")

    if erros:
        for e in erros:
            print(f"falhou: {e}")
        raise SystemExit(1)

    print("integridade ok")


if __name__ == "__main__":
    conn = montar()
    testar_integridade(conn)
    conn.close()
    print(f"banco criado em {DB_PATH}")
