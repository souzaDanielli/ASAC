from pathlib import Path

import pandas as pd


def ler_noticias(caminho):
    df = pd.read_csv(caminho, sep=";", on_bad_lines="skip")
    df.columns = [c.replace('"', "").strip() for c in df.columns]
    df = df.rename(columns={
        "Título": "titulo",
        "Subtítulo": "subtitulo",
        "Data": "data",
        "Texto": "texto",
        "Classe": "classe",
    })
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y %H:%M")
    return df


def ler_precos(caminho, praca):
    df = pd.read_csv(caminho, sep=",", decimal=",")
    df.columns = [c.replace('"', "").strip() for c in df.columns]
    col_brl = [c for c in df.columns if "R$" in c][0]
    col_usd = [c for c in df.columns if "US$" in c][0]
    df = df.rename(columns={"Data": "data", col_brl: "valor_brl", col_usd: "valor_usd"})
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["praca"] = praca
    return df[["data", "praca", "valor_brl", "valor_usd"]]


def remover_duplicados(df):
    return df.drop_duplicates(subset="titulo", keep="first")


def separar_classe(df):
    partes = df["classe"].str.lower().str.split(" ", expand=True)
    df["mercado"] = partes[1]
    df["sentimento"] = partes[2]
    return df.drop(columns="classe")


def recuperar_link(df, caminho_bruto):
    bruto = pd.read_csv(caminho_bruto, sep=";", on_bad_lines="skip")
    bruto.columns = [c.replace('"', "").strip() for c in bruto.columns]
    links = bruto.drop_duplicates(subset="Título").set_index("Título")["Link"]
    df["link"] = df["titulo"].map(links)
    return df


def marcar_origem(df, caminho_amostra):
    amostra = pd.read_csv(caminho_amostra, sep=",", on_bad_lines="skip")
    amostra.columns = [c.replace('"', "").strip() for c in amostra.columns]
    titulos_manuais = set(amostra.dropna(subset=["Análise Manual"])["Título"])
    df["origem_rotulo"] = df["titulo"].apply(lambda t: "manual" if t in titulos_manuais else "modelo")
    return df


def carregar_tudo(pasta_data):
    pasta_data = Path(pasta_data)

    noticias = ler_noticias(pasta_data / "noticias_classificadas_todas.csv")
    noticias = remover_duplicados(noticias)
    noticias = separar_classe(noticias)
    noticias = recuperar_link(noticias, pasta_data / "noticias_soja_canal_rural.csv")
    noticias = marcar_origem(noticias, pasta_data / "todas-noticias-e-amostra-classificada.csv")

    parana = ler_precos(pasta_data / "cepea-consulta-parana.csv", "parana")
    paranagua = ler_precos(pasta_data / "cepea-consulta-paranagua.csv", "paranagua")
    precos = pd.concat([parana, paranagua], ignore_index=True)

    return noticias, precos


if __name__ == "__main__":
    noticias, precos = carregar_tudo(Path(__file__).resolve().parents[2] / "data")

    print(f"noticias: {len(noticias)}")
    print(noticias["mercado"].value_counts())
    print(noticias["sentimento"].value_counts())
    print(noticias["origem_rotulo"].value_counts())
    print(f"links vazios: {noticias['link'].isna().sum()}")
    print(f"precos: {len(precos)}")
