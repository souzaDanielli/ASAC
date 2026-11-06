import io
from datetime import datetime
from pathlib import Path

import httpx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

BASE_URL = "http://localhost:8000/api"
SAIDA_PDF = Path(__file__).resolve().parents[2] / "relatorio_asac.pdf"


def _get_client():
    """Retorna um cliente HTTPx se o servidor estiver rodando, ou TestClient in-process se estiver offline."""
    try:
        resp = httpx.get("http://localhost:8000/api/health", timeout=1.5)
        if resp.status_code == 200:
            return httpx.Client(base_url="http://localhost:8000/api", timeout=30.0)
    except Exception:
        pass

    # Modo autônomo offline: executa as rotas diretamente via FastAPI TestClient
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app, base_url="http://testserver/api")


def buscar_dados_relatorio(client):
    resp = client.get("/reports")
    resp.raise_for_status()
    return resp.json()


def buscar_resumo(client, praca):
    resp = client.get("/analysis/summary", params={"praca": praca})
    resp.raise_for_status()
    return resp.json()


def buscar_grafico(client, rota):
    resp = client.get(f"/reports/chart/{rota}")
    resp.raise_for_status()
    return io.BytesIO(resp.content)


def _data_formatada(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y às %H:%M")
    except ValueError:
        return iso


def _quebrar_linha(texto, largura):
    if not texto:
        return []
    palavras = str(texto).split()
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

    for linha in _quebrar_linha(dados.get("titulo", "Relatório ASAC"), 45):
        eixo.text(margem_esq, y, linha, fontsize=20, fontweight="bold", color=COR_TITULO, va="top")
        y -= 0.05
    y -= 0.005
    eixo.text(margem_esq, y, f"Gerado em {_data_formatada(dados.get('gerado_em', ''))}", fontsize=10, color="#777777", va="top")
    y -= 0.03
    eixo.axhline(y, xmin=margem_esq, xmax=1 - margem_esq, color=COR_LINHA, linewidth=1)
    y -= 0.045

    periodo = dados.get("periodo_dados", {})
    indicadores = (
        f"{dados.get('total_noticias', 0):,} notícias analisadas  •  {dados.get('total_pregoes', 0):,} pregões CEPEA  •  "
        f"período {periodo.get('noticias_inicio', '')} a {periodo.get('noticias_fim', '')}"
    ).replace(",", ".")
    eixo.text(margem_esq, y, indicadores, fontsize=9.5, color=COR_DESTAQUE, fontweight="bold", va="top")
    y -= 0.055

    nomes_praca = {"parana": "Mercado interno — Paraná", "paranagua": "Mercado externo — Paranaguá"}
    for praca, resumo in resumos_por_praca.items():
        eixo.text(margem_esq, y, nomes_praca.get(praca, praca), fontsize=12.5, fontweight="bold", color=COR_TITULO, va="top")
        y -= 0.032
        texto_resumo = resumo.get("texto", "")
        for linha in _quebrar_linha(texto_resumo, largura_coluna):
            eixo.text(margem_esq, y, linha, fontsize=9.5, color=COR_TEXTO, va="top")
            y -= 0.025
        y -= 0.02

    eixo.axhline(y, xmin=margem_esq, xmax=1 - margem_esq, color=COR_LINHA, linewidth=1)
    y -= 0.045

    eixo.text(margem_esq, y, "Métricas do modelo de classificação", fontsize=12.5, fontweight="bold", color=COR_TITULO, va="top")
    y -= 0.035
    for m in dados.get("metricas_modelo", []):
        cabecalho = f"▸ {m.get('estrategia', '')}"
        for linha in _quebrar_linha(cabecalho, largura_coluna - 4):
            eixo.text(margem_esq, y, linha, fontsize=9.5, fontweight="bold", color=COR_TEXTO, va="top")
            y -= 0.025
        acc = f"{m['acuracia']:.2%}" if m.get('acuracia') is not None else "N/D"
        f1_sc = f"{m['f1']:.2%}" if m.get('f1') is not None else "N/D"
        detalhe = (
            f"acurácia {acc}  ·  F1 macro {f1_sc}  ·  "
            f"{m.get('amostras', 0)} amostras  ·  {m.get('metodo_avaliacao', '')}"
        )
        for linha in _quebrar_linha(detalhe, largura_coluna - 4):
            eixo.text(margem_esq + 0.025, y, linha, fontsize=9, color="#555555", va="top")
            y -= 0.023
        y -= 0.015

    eixo.text(
        margem_esq, 0.03, "Estudo exploratório baseado em correlações estatísticas sem pressuposição de causalidade.",
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
    client = _get_client()
    dados = buscar_dados_relatorio(client)
    resumos_por_praca = {praca: buscar_resumo(client, praca) for praca in ("parana", "paranagua")}
    png_serie = buscar_grafico(client, "timeseries")
    png_correlacao = buscar_grafico(client, "correlation")

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
