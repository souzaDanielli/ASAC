import io
from datetime import datetime
from pathlib import Path

import httpx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

BASE_URL = "http://localhost:8000/api"
SAIDA_PDF = Path(__file__).resolve().parents[2] / "relatorio_asac.pdf"


def buscar_dados_relatorio():
    resp = httpx.get(f"{BASE_URL}/reports", timeout=30)
    resp.raise_for_status()
    return resp.json()


def buscar_resumo(praca):
    resp = httpx.get(f"{BASE_URL}/analysis/summary", params={"praca": praca}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def buscar_grafico(rota):
    resp = httpx.get(f"{BASE_URL}/reports/chart/{rota}", timeout=30)
    resp.raise_for_status()
    return io.BytesIO(resp.content)


def _data_formatada(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y às %H:%M")
    except ValueError:
        return iso


def _quebrar_linha(texto, largura):
    palavras = texto.split()
    linhas, atual = [], ""
    for palavra in palavras:
        if len(atual) + len(palavra) + 1 > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    if atual:
        linhas.append(atual)
    return linhas


COR_TITULO = "#1a3c34"
COR_DESTAQUE = "#2e7d32"
COR_TEXTO = "#333333"
COR_LINHA = "#cccccc"


def pagina_texto(dados, resumos_por_praca):
    fig = plt.figure(figsize=(11, 8.5))
    eixo = fig.add_axes((0, 0, 1, 1))
    eixo.axis("off")
    eixo.set_xlim(0, 1)
    eixo.set_ylim(0, 1)

    margem_esq = 0.08
    largura_coluna = 100
    y = 0.93

    for linha in _quebrar_linha(dados["titulo"], 45):
        eixo.text(margem_esq, y, linha, fontsize=20, fontweight="bold", color=COR_TITULO, va="top")
        y -= 0.05
    y -= 0.005
    eixo.text(margem_esq, y, f"Gerado em {_data_formatada(dados['gerado_em'])}", fontsize=10, color="#777777", va="top")
    y -= 0.03
    eixo.axhline(y, xmin=margem_esq, xmax=1 - margem_esq, color=COR_LINHA, linewidth=1)
    y -= 0.045

    indicadores = (
        f"{dados['total_noticias']} notícias analisadas  •  {dados['total_pregoes']} pregões CEPEA  •  "
        f"período {dados['periodo_dados']['noticias_inicio']} a {dados['periodo_dados']['noticias_fim']}"
    )
    eixo.text(margem_esq, y, indicadores, fontsize=9.5, color=COR_DESTAQUE, fontweight="bold", va="top")
    y -= 0.055

    nomes_praca = {"parana": "Mercado interno — Paraná", "paranagua": "Mercado externo — Paranaguá"}
    for praca, resumo in resumos_por_praca.items():
        eixo.text(margem_esq, y, nomes_praca.get(praca, praca), fontsize=12.5, fontweight="bold", color=COR_TITULO, va="top")
        y -= 0.032
        for linha in _quebrar_linha(resumo["texto"], largura_coluna):
            eixo.text(margem_esq, y, linha, fontsize=9.5, color=COR_TEXTO, va="top")
            y -= 0.025
        y -= 0.02

    eixo.axhline(y, xmin=margem_esq, xmax=1 - margem_esq, color=COR_LINHA, linewidth=1)
    y -= 0.045

    eixo.text(margem_esq, y, "Métricas do modelo de classificação", fontsize=12.5, fontweight="bold", color=COR_TITULO, va="top")
    y -= 0.035
    for m in dados["metricas_modelo"]:
        cabecalho = f"▸ {m['estrategia']}"
        for linha in _quebrar_linha(cabecalho, largura_coluna - 4):
            eixo.text(margem_esq, y, linha, fontsize=9.5, fontweight="bold", color=COR_TEXTO, va="top")
            y -= 0.025
        detalhe = (
            f"acurácia {m['acuracia']:.2%}  ·  F1 macro {m['f1']:.2%}  ·  "
            f"{m['amostras']} amostras  ·  {m['metodo_avaliacao']}"
        )
        for linha in _quebrar_linha(detalhe, largura_coluna - 4):
            eixo.text(margem_esq + 0.025, y, linha, fontsize=9, color="#555555", va="top")
            y -= 0.023
        y -= 0.015

    eixo.text(
        margem_esq, 0.03, "Estudo exploratório.",
        fontsize=8, color="#999999", style="italic", va="bottom",
    )
    return fig


def pagina_imagem(png_bytes, titulo):
    imagem = mpimg.imread(png_bytes, format="png")
    fig, eixo = plt.subplots(figsize=(11, 8.5))
    eixo.imshow(imagem)
    eixo.set_title(titulo)
    eixo.axis("off")
    fig.tight_layout()
    return fig


def montar_relatorio(saida=SAIDA_PDF):
    dados = buscar_dados_relatorio()
    resumos_por_praca = {praca: buscar_resumo(praca) for praca in ("parana", "paranagua")}
    png_serie = buscar_grafico("timeseries")
    png_correlacao = buscar_grafico("correlation")

    with PdfPages(saida) as pdf:
        pdf.savefig(pagina_texto(dados, resumos_por_praca))
        plt.close()

        pdf.savefig(pagina_imagem(png_serie, "Série temporal"))
        plt.close()

        pdf.savefig(pagina_imagem(png_correlacao, "Correlação por defasagem"))
        plt.close()

    return saida


if __name__ == "__main__":
    caminho = montar_relatorio()
    print(f"relatorio gerado em {caminho}")
