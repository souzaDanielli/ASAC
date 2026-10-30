import pandas as pd

from app.services.analise import correlacoes_por_defasagem


def test_correlacao_lag0_bate_com_valor_calculado_a_mao():
    # x = [1,2,3], y = [1,3,2] -> media_x=2, media_y=2
    # covariancia = (-1*-1)+(0*1)+(1*0) = 1 ; var_x=2, var_y=2 -> pearson = 1/raiz(4) = 0.5
    sentimento = pd.DataFrame({
        "data": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "indice_sentimento": [1, 2, 3],
    })
    var_pct_por_data = pd.Series(
        [1, 3, 2],
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )

    tabela = correlacoes_por_defasagem(sentimento, var_pct_por_data, lags=[0])

    linha = tabela.iloc[0]
    assert linha["defasagem"] == 0
    assert linha["amostras"] == 3
    assert round(linha["pearson"], 4) == 0.5


def test_defasagem_descarta_amostra_quando_dia_futuro_nao_tem_pregao():
    # relacao perfeitamente linear sentimento -> var_pct do mesmo dia
    datas = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"])
    sentimento = pd.DataFrame({"data": datas, "indice_sentimento": [1, 2, 3, 4, 5]})

    # nao existe pregao no dia 2024-01-06 (fim de semana/feriado)
    var_pct_por_data = pd.Series([10, 20, 30, 40, 50], index=datas)

    tabela = correlacoes_por_defasagem(sentimento, var_pct_por_data, lags=[0, 1])

    lag0 = tabela[tabela["defasagem"] == 0].iloc[0]
    lag1 = tabela[tabela["defasagem"] == 1].iloc[0]

    assert lag0["amostras"] == 5
    assert round(lag0["pearson"], 4) == 1.0

    # defasagem 1 perde a ultima amostra (2024-01-05 -> 2024-01-06, sem pregao)
    assert lag1["amostras"] == 4
    assert round(lag1["pearson"], 4) == 1.0
