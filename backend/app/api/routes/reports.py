import sqlite3
from datetime import datetime
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.schemas.extra import ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=ReportResponse, summary="Relatório analítico consolidado")
def get_report(db: sqlite3.Connection = Depends(get_db)):
    total_noticias = db.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    total_pregoes = db.execute("SELECT COUNT(DISTINCT data) FROM precos").fetchone()[0]

    min_max_noticias = db.execute("SELECT MIN(data_dia), MAX(data_dia) FROM noticias").fetchone()
    min_max_precos = db.execute("SELECT MIN(data), MAX(data) FROM precos").fetchone()

    metricas_rows = db.execute("SELECT * FROM metricas_modelo").fetchall()
    metricas = [dict(r) for r in metricas_rows]

    resumo_cache = db.execute(
        "SELECT texto FROM resumos ORDER BY id DESC LIMIT 1"
    ).fetchone()
    texto_resumo = (
        resumo_cache["texto"]
        if resumo_cache
        else "Relatório consolidado com a série histórica de notícias agrícolas da soja e cotações CEPEA."
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
