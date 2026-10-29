import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.schemas.extra import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse, summary="Status de saúde da API e banco de dados")
def get_health(db: sqlite3.Connection = Depends(get_db)):
    try:
        total_noticias = db.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
        total_precos = db.execute("SELECT COUNT(*) FROM precos").fetchone()[0]
        return HealthResponse(
            status="online",
            database_status="connected",
            total_noticias=total_noticias,
            total_precos=total_precos
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar integridade do banco de dados: {str(e)}"
        )
