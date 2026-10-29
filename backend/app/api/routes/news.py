import sqlite3
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.database import get_db
from app.schemas.extra import PaginatedNewsResponse

router = APIRouter(prefix="/news", tags=["News"])

@router.get("", response_model=PaginatedNewsResponse, summary="Listagem de notícias com paginação e filtros")
def list_news(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    mercado: Optional[str] = Query(default=None, description="Filtro por mercado (interno ou externo)"),
    sentimento: Optional[str] = Query(default=None, description="Filtro por sentimento (positivo, negativo, neutro)"),
    data_inicio: Optional[str] = Query(default=None, description="Data início no formato YYYY-MM-DD"),
    data_fim: Optional[str] = Query(default=None, description="Data fim no formato YYYY-MM-DD"),
    origem_rotulo: Optional[str] = Query(default=None, description="Origem do rótulo (manual ou modelo)"),
    db: sqlite3.Connection = Depends(get_db)
):
    query = "SELECT * FROM noticias WHERE 1=1"
    params = []

    if mercado:
        query += " AND LOWER(mercado) = LOWER(?)"
        params.append(mercado)

    if sentimento:
        query += " AND LOWER(sentimento) = LOWER(?)"
        params.append(sentimento)

    if data_inicio:
        query += " AND data_dia >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND data_dia <= ?"
        params.append(data_fim)

    if origem_rotulo:
        query += " AND LOWER(origem_rotulo) = LOWER(?)"
        params.append(origem_rotulo)

    count_query = f"SELECT COUNT(*) FROM ({query})"
    total = db.execute(count_query, params).fetchone()[0]

    offset = (page - 1) * page_size
    query += " ORDER BY data DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])

    rows = db.execute(query, params).fetchall()
    items = [dict(row) for row in rows]
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedNewsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )
