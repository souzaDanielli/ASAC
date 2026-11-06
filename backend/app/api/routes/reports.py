import sqlite3
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.schemas.extra import ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=ReportResponse, summary="Relatório analítico consolidado")
def get_report(db: sqlite3.Connection = Depends(get_db)):
    try:
        total_noticias = db.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
        total_pregoes = db.execute("SELECT COUNT(DISTINCT data) FROM precos").fetchone()[0]

        min_max_noticias = db.execute("SELECT MIN(data_dia), MAX(data_dia) FROM noticias").fetchone()
        min_max_precos = db.execute("SELECT MIN(data), MAX(data) FROM precos").fetchone()

        metricas_rows = db.execute("SELECT * FROM metricas_modelo").fetchall()
        metricas = [dict(r) for r in metricas_rows]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório consolidado: {str(e)}"
        )

    texto_resumo = (
        f"Relatório executivo integrando o acompanhamento temporal de {total_noticias.toLocaleString() if hasattr(total_noticias, 'toLocaleString') else f'{total_noticias:,}'.replace(',', '.')} notícias agrícolas "
        f"especializadas do setor da soja com {f'{total_pregoes:,}'.replace(',', '.')} pregões de fechamento do indicador CEPEA/ESALQ "
        f"(mercado interno do Paraná e porto exportador de Paranaguá) no intervalo de {min_max_noticias[0]} a {min_max_noticias[1]}. "
        f"A estrutura investiga a concomitância estatística entre a polaridade líquida do sentimento textual e a dinâmica de preços, "
        f"avaliando defasagens temporais sem pressuposição de causalidade determinística."
    )

    return ReportResponse(
        titulo="Relatório Consolidado de Sentimento de Notícias e Preços CEPEA",
        gerado_em=datetime.now().isoformat(),
        resumo_geral=texto_resumo,
        total_noticias=total_noticias,
        total_pregoes=total_pregoes,
        periodo_dados={
            "noticias_inicio": min_max_noticias[0],
            "noticias_fim": min_max_noticias[1],
            "precos_inicio": min_max_precos[0],
            "precos_fim": min_max_precos[1]
        },
        metricas_modelo=metricas,
        insights_principais=[
            "6.320 notícias tratadas e associadas com o próximo pregão útil do CEPEA.",
            "Preços de fechamento diários cobrindo o mercado interno (Paraná) e porto exportador (Paranaguá).",
            "Cálculo de índice de sentimento diário e semanal pronto para análise estatística.",
            "As correlações estatísticas investigam defasagens temporais sem pressuposição de causalidade determinística."
        ]
    )
