import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.database import get_db
from app.schemas.extra import CorrelationResponse, CorrelationItem
from app.services.llm_service import obter_ou_gerar_resumo

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/timeseries", summary="Série temporal de Preço x Sentimento (diário ou semanal)")
def get_timeseries(
    frequencia: str = Query(default="diario", pattern="^(diario|semanal)$", description="Frequência: 'diario' ou 'semanal'"),
    mercado: Optional[str] = Query(default=None, description="Mercado: interno ou externo"),
    data_inicio: Optional[str] = Query(default=None, description="Data início"),
    data_fim: Optional[str] = Query(default=None, description="Data fim"),
    db: sqlite3.Connection = Depends(get_db)
) -> List[Dict[str, Any]]:
    if frequencia == "diario":
        if mercado:
            query = """
            SELECT
                data,
                mercado,
                praca,
                qtd_total,
                indice_sentimento,
                valor_brl,
                valor_usd,
                var_pct
            FROM vw_preco_x_sentimento
            WHERE LOWER(mercado) = LOWER(?)
            """
            params = [mercado]
        else:
            # Agrupa por dia para não duplicar linhas quando mercado for 'todos'
            query = """
            SELECT
                data,
                'todos' AS mercado,
                'todos' AS praca,
                SUM(qtd_total) AS qtd_total,
                ROUND(AVG(indice_sentimento), 4) AS indice_sentimento,
                ROUND(AVG(valor_brl), 2) AS valor_brl,
                ROUND(AVG(valor_usd), 2) AS valor_usd,
                ROUND(AVG(var_pct), 2) AS var_pct
            FROM vw_preco_x_sentimento
            WHERE 1=1
            """
            params = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        if not mercado:
            query += " GROUP BY data"

        query += " ORDER BY data ASC"
        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    else:
        # Frequência semanal agregando Preço e Sentimento
        if mercado:
            query = """
            SELECT
                strftime('%Y-W%W', data) AS semana,
                MIN(data) AS data,
                MIN(data) AS semana_inicio,
                MAX(data) AS semana_fim,
                mercado,
                SUM(qtd_total) AS qtd_total,
                ROUND(AVG(indice_sentimento), 4) AS indice_sentimento,
                ROUND(AVG(valor_brl), 2) AS valor_brl,
                ROUND(AVG(valor_usd), 2) AS valor_usd,
                ROUND(AVG(var_pct), 2) AS var_pct
            FROM vw_preco_x_sentimento
            WHERE LOWER(mercado) = LOWER(?)
            """
            params = [mercado]
        else:
            query = """
            SELECT
                strftime('%Y-W%W', data) AS semana,
                MIN(data) AS data,
                MIN(data) AS semana_inicio,
                MAX(data) AS semana_fim,
                'todos' AS mercado,
                SUM(qtd_total) AS qtd_total,
                ROUND(AVG(indice_sentimento), 4) AS indice_sentimento,
                ROUND(AVG(valor_brl), 2) AS valor_brl,
                ROUND(AVG(valor_usd), 2) AS valor_usd,
                ROUND(AVG(var_pct), 2) AS var_pct
            FROM vw_preco_x_sentimento
            WHERE 1=1
            """
            params = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        query += " GROUP BY semana ORDER BY semana ASC"
        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]


from app.services.analise import rodar as calcular_correlacoes
from app.services.analise import PRACA_POR_MERCADO

@router.get("/correlation", response_model=CorrelationResponse, summary="Coeficientes de correlação (Pearson/Spearman com defasagens de 0 a 5 dias)")
def get_correlation(
    mercado: Optional[str] = Query(default=None, description="Mercado (interno, externo)"),
    praca: Optional[str] = Query(default=None, description="Praça (parana, paranagua)"),
    db: sqlite3.Connection = Depends(get_db)
):
    tabelas_correlacao = calcular_correlacoes()
    resultados = []

    for merc, df in tabelas_correlacao.items():
        praca_mercado = PRACA_POR_MERCADO[merc]

        if mercado and merc.lower() != mercado.lower():
            continue
        if praca and praca_mercado.lower() != praca.lower():
            continue

        for _, row in df.iterrows():
            resultados.append(
                CorrelationItem(
                    mercado=merc,
                    praca=praca_mercado,
                    defasagem_dias=int(row["defasagem"]),
                    pearson=round(float(row["pearson"]), 4) if pd.notnull(row["pearson"]) else None,
                    spearman=round(float(row["spearman"]), 4) if pd.notnull(row["spearman"]) else None,
                    amostras=int(row["amostras"]) if pd.notnull(row["amostras"]) else None
                )
            )

    return CorrelationResponse(
        status="concluido",
        descricao="Cálculo das correlações de Pearson e Spearman com defasagens de 0 a 5 dias cortando a série em 03/09/2026.",
        resultados=resultados
    )


@router.get("/summary", summary="Resumo analítico gerado por IA com cache")
def get_summary(
    periodo: str = Query(default="geral", description="Identificador do período (ex: 2023-2026, 2026-09)"),
    praca: str = Query(default="parana", description="Praça: parana ou paranagua"),
    db: sqlite3.Connection = Depends(get_db)
):
    stats = db.execute(
        """
        SELECT
            COUNT(*) as total,
            AVG(indice_sentimento) as media_sentimento,
            AVG(var_pct) as media_var_preco
        FROM vw_preco_x_sentimento
        WHERE praca = ?
        """,
        (praca,)
    ).fetchone()

    total_noticias = stats["total"] if stats else 0
    indice_medio = stats["media_sentimento"] if (stats and stats["media_sentimento"] is not None) else 0.0
    var_preco_medio = stats["media_var_preco"] if (stats and stats["media_var_preco"] is not None) else 0.0

    # Obter correlações calculadas para complementar o resumo
    mercado_alvo = "interno" if praca.lower() == "parana" else "externo"
    tabelas_correlacao = calcular_correlacoes()
    df_merc = tabelas_correlacao.get(mercado_alvo)

    melhor_lag = 0
    maior_pearson = 0.0
    if df_merc is not None and not df_merc.empty:
        idx_max = df_merc["pearson"].abs().idxmax()
        melhor_lag = int(df_merc.loc[idx_max, "defasagem"])
        maior_pearson = round(float(df_merc.loc[idx_max, "pearson"]), 4)

    agregados = {
        "total_noticias": total_noticias,
        "indice_sentimento_medio": round(float(indice_medio), 4),
        "var_pct_preco_medio": round(float(var_preco_medio), 4),
        "melhor_defasagem_dias": melhor_lag,
        "maior_correlacao_pearson": maior_pearson
    }

    return obter_ou_gerar_resumo(db=db, periodo=periodo, praca=praca, dados_agregados=agregados)
