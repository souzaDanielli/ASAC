import io
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, Response

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
    fig = grafico_serie_temporal(db)
    return _figura_para_png(fig)


@router.get("/correlation", summary="Gráfico de correlação por defasagem em PNG")
def chart_correlation():
    fig = grafico_correlacao()
    return _figura_para_png(fig)
