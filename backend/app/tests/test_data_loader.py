from pathlib import Path

import pandas as pd
import pytest

from app.services.data_loader import carregar_tudo, remover_duplicados, separar_classe

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def test_remover_duplicados_mantem_so_a_primeira_ocorrencia():
    df = pd.DataFrame({"titulo": ["a", "b", "a", "c"], "valor": [1, 2, 3, 4]})
    resultado = remover_duplicados(df)
    assert len(resultado) == 3
    assert resultado[resultado["titulo"] == "a"]["valor"].iloc[0] == 1


def test_separar_classe_divide_mercado_e_sentimento():
    df = pd.DataFrame({"classe": ["mercado interno positivo", "mercado externo negativo"]})
    resultado = separar_classe(df)
    assert list(resultado["mercado"]) == ["interno", "externo"]
    assert list(resultado["sentimento"]) == ["positivo", "negativo"]
    assert "classe" not in resultado.columns


@pytest.mark.skipif(not DATA_DIR.exists(), reason="pasta data/ nao encontrada")
def test_carregar_tudo_bate_com_as_contagens_esperadas():
    noticias, precos = carregar_tudo(DATA_DIR)

    assert len(noticias) == 6320
    assert len(noticias) == noticias["titulo"].nunique()  # sem duplicados

    contagem_mercado = noticias["mercado"].value_counts()
    assert contagem_mercado["interno"] == 4509
    assert contagem_mercado["externo"] == 1811

    assert len(precos) == 2834
    assert set(precos["praca"].unique()) == {"parana", "paranagua"}

    origens_validas = {"manual", "modelo"}
    assert set(noticias["origem_rotulo"].unique()) <= origens_validas
    assert (noticias["origem_rotulo"] == "manual").sum() == 611
