import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.schemas.preco import PrecoResponse

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.get("", response_model=List[PrecoResponse], summary="Série histórica de preços CEPEA por praça e intervalo de datas")
def list_prices(
    praca: Optional[str] = Query(default=None, pattern="^(?i)(parana|paranagua)$", description="Praça: parana ou paranagua"),
    data_inicio: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data fim (YYYY-MM-DD)"),
    limit: int = Query(default=1000, ge=1, le=5000, description="Limite máximo de registros"),
    db: sqlite3.Connection = Depends(get_db)
):
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(status_code=400, detail="O parâmetro 'data_inicio' não pode ser posterior a 'data_fim'.")

    query = "SELECT data, praca, valor_brl, valor_usd, var_pct FROM precos WHERE 1=1"
    params = []

    if praca:
        query += " AND LOWER(praca) = LOWER(?)"
        params.append(praca)

    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)

    query += " ORDER BY data ASC LIMIT ?"
    params.append(limit)

    try:
        rows = db.execute(query, params).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar preços no banco de dados: {str(e)}")

    return [dict(row) for row in rows]
