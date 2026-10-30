import pandas as pd
import matplotlib.pyplot as plt

from app.services.analise import rodar as calcular_correlacoes, CORTE


def carregar_serie_semanal(conn, mercado):
    df = pd.read_sql(
        """
        SELECT data, indice_sentimento, valor_brl
        FROM vw_preco_x_sentimento
        WHERE mercado = ? AND data <= ? AND valor_brl IS NOT NULL
        ORDER BY data
        """,
        conn,
        params=(mercado, CORTE),
    )
    df["data"] = pd.to_datetime(df["data"])
    return df.set_index("data").resample("W").mean(numeric_only=True)


def grafico_serie_temporal(conn):
    fig, eixos = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    fig.suptitle("Índice de sentimento x Preço CEPEA (média semanal)")

    for eixo, mercado in zip(eixos, ("interno", "externo")):
        semanal = carregar_serie_semanal(conn, mercado)

        eixo.set_title(f"Mercado {mercado}")
        eixo.plot(semanal.index, semanal["indice_sentimento"], color="tab:blue", label="Índice de sentimento")
        eixo.set_ylabel("Índice de sentimento", color="tab:blue")
        eixo.axhline(0, color="gray", linewidth=0.5)

        eixo_preco = eixo.twinx()
        eixo_preco.plot(semanal.index, semanal["valor_brl"], color="tab:red", label="Preço (R$)")
        eixo_preco.set_ylabel("Preço R$", color="tab:red")

    eixos[-1].set_xlabel("Data")
    fig.tight_layout()
    return fig


def grafico_correlacao():
    tabelas = calcular_correlacoes()
    fig, eixo = plt.subplots(figsize=(9, 5))

    largura = 0.35
    for i, (mercado, df) in enumerate(tabelas.items()):
        posicoes = df["defasagem"] + (i - 0.5) * largura
        eixo.bar(posicoes, df["pearson"], width=largura, label=f"Pearson ({mercado})")

    eixo.axhline(0, color="gray", linewidth=0.5)
    eixo.set_xlabel("Defasagem (dias corridos)")
    eixo.set_ylabel("Coeficiente de Pearson")
    eixo.set_title("Correlação sentimento x variação de preço, por defasagem")
    eixo.legend()
    fig.tight_layout()
    return fig
