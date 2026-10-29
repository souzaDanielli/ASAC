import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

def gerar_resumo_template(metricas: Dict[str, Any]) -> str:
    """Gera resumo analítico a partir de template sem depender de chave de API externa."""
    total_noticias = metricas.get("total_noticias", 0)
    indice_medio = metricas.get("indice_sentimento_medio", 0.0)
    periodo = metricas.get("periodo", "Período analisado")
    praca = metricas.get("praca", "Geral")
    melhor_lag = metricas.get("melhor_defasagem_dias", 0)
    maior_pearson = metricas.get("maior_correlacao_pearson", 0.0)

    polaridade = "positivo" if indice_medio > 0.05 else ("negativo" if indice_medio < -0.05 else "neutro")

    detalhe_correlacao = (
        f"A análise estatística indicou uma correlação máxima de Pearson de {maior_pearson:.4f} "
        f"com defasagem temporal de {melhor_lag} dia(s) em relação ao preço CEPEA. "
        if maior_pearson != 0.0 else ""
    )

    texto = (
        f"Relatório de Análise de Sentimento ({periodo} - Praça: {praca}). "
        f"Foram analisadas {total_noticias} notícias no intervalo especificado, resultando em um índice de "
        f"sentimento consolidado de {indice_medio:.4f}, classificado como predominantemente {polaridade}. "
        f"{detalhe_correlacao}"
        f"Importante: Esta análise baseia-se em correlações estatísticas entre as variáveis observadas; "
        f"não é possível inferir que o sentimento das notícias causou diretamente as variações nos preços de fechamento CEPEA."
    )
    return texto

def obter_ou_gerar_resumo(
    db: sqlite3.Connection,
    periodo: str,
    praca: str,
    dados_agregados: Dict[str, Any]
) -> Dict[str, Any]:
    params_key = json.dumps({"periodo": periodo, "praca": praca}, sort_keys=True)

    # Tenta recuperar do cache (tabela resumos)
    cache = db.execute(
        "SELECT id, periodo, parametros, texto, modelo_llm, gerado_em FROM resumos WHERE periodo = ? AND parametros = ? ORDER BY id DESC LIMIT 1",
        (periodo, params_key)
    ).fetchone()

    if cache:
        return {
            "fonte": "cache",
            "periodo": cache["periodo"],
            "texto": cache["texto"],
            "modelo_llm": cache["modelo_llm"],
            "gerado_em": cache["gerado_em"]
        }

    gemini_key = os.getenv("GEMINI_API_KEY")
    modelo_utilizado = "template_interno"
    texto_gerado = ""

    metricas = {
        "periodo": periodo,
        "praca": praca,
        "total_noticias": dados_agregados.get("total_noticias", 0),
        "indice_sentimento_medio": dados_agregados.get("indice_sentimento_medio", 0.0),
        "var_pct_preco_medio": dados_agregados.get("var_pct_preco_medio", 0.0),
        "melhor_defasagem_dias": dados_agregados.get("melhor_defasagem_dias", 0),
        "maior_correlacao_pearson": dados_agregados.get("maior_correlacao_pearson", 0.0)
    }

    if gemini_key:
        try:
            import requests
            prompt = (
                f"Você é um assistente de análise econômica. Com base exclusivamente nos números agregados a seguir: {json.dumps(metricas)}, "
                f"produza um resumo analítico objetivo de até 2 parágrafos em português. "
                f"REGRA MANDATÓRIA: É terminantemente proibido afirmar ou insinuar causalidade direta, "
                f"ou seja, nunca afirme que o sentimento causou ou provocou a variação do preço CEPEA. Use termos como correlação ou concomitância."
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={gemini_key}"
            resp = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                texto_gerado = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                modelo_utilizado = "gemini-3.5-flash-lite"
            else:
                texto_gerado = gerar_resumo_template(metricas)
                modelo_utilizado = "template_interno_fallback"
        except Exception:
            texto_gerado = gerar_resumo_template(metricas)
            modelo_utilizado = "template_interno_fallback"
    else:
        texto_gerado = gerar_resumo_template(metricas)
        modelo_utilizado = "template_interno"

    gerado_em = datetime.now().isoformat()

    # Salva no banco
    db.execute(
        """
        INSERT INTO resumos (periodo, parametros, texto, modelo_llm, gerado_em)
        VALUES (?, ?, ?, ?, ?)
        """,
        (periodo, params_key, texto_gerado, modelo_utilizado, gerado_em)
    )
    db.commit()

    return {
        "fonte": "gerado",
        "periodo": periodo,
        "texto": texto_gerado,
        "modelo_llm": modelo_utilizado,
        "gerado_em": gerado_em
    }
