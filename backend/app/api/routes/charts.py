import io
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.database import get_db
from app.services.graficos import grafico_serie_temporal, grafico_correlacao

router = APIRouter(prefix="/reports/chart", tags=["Reports"])


def _figura_para_png(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="image/png")


@router.get("/timeseries", summary="Gráfico de série temporal (sentimento x preço) em PNG")
def chart_timeseries(db: sqlite3.Connection = Depends(get_db)):
    try:
        fig = grafico_serie_temporal(db)
        return _figura_para_png(fig)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar gráfico de série temporal: {str(e)}"
        )


@router.get("/correlation", summary="Gráfico de correlação por defasagem em PNG")
def chart_correlation():
    try:
        fig = grafico_correlacao()
        return _figura_para_png(fig)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar gráfico de correlação: {str(e)}"
        )
