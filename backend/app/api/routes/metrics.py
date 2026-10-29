import sqlite3
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.core.database import get_db

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/model", summary="Métricas gerais e por classe do modelo de classificação")
def get_model_metrics(db: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    metricas_gerais = db.execute(
        """
        SELECT estrategia, acuracia, precisao, recall, f1, tempo_execucao, amostras, metodo_avaliacao
        FROM metricas_modelo
        """
    ).fetchall()

    metricas_classes = db.execute(
        """
        SELECT estrategia, classe, precisao, recall, f1, suporte
        FROM metricas_por_classe
        """
    ).fetchall()

    # Caso o módulo de métricas ainda esteja sendo populado pelo time de ML/análise
    dados_gerais = [dict(row) for row in metricas_gerais]
    dados_classes = [dict(row) for row in metricas_classes]

    status_populacao = "completo" if (dados_gerais or dados_classes) else "aguardando_gravacao_modelo"

    return {
        "status": status_populacao,
        "estrategia_padrao": "Estratégia 2 (Hierárquica / Validação Cruzada)",
        "metricas_gerais": dados_gerais,
        "metricas_por_classe": dados_classes
    }
