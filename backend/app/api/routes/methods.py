from fastapi import APIRouter
from app.schemas.extra import MethodsResponse, EstrategiaInfo, PreprocessamentoInfo

router = APIRouter(prefix="/methods", tags=["Methods"])

@router.get("", response_model=MethodsResponse, summary="Estratégias testadas e pipeline de pré-processamento")
def get_methods():
    return MethodsResponse(
        estrategias_testadas=[
            EstrategiaInfo(
                id="estrategia_1",
                nome="Classificação Direta Multiclasse",
                descricao="Classificação direta do texto da notícia em 6 classes combinadas (mercado x sentimento).",
                modelo="TF-IDF + Classificador supervisionado / LLM Few-shot"
            ),
            EstrategiaInfo(
                id="estrategia_2",
                nome="Classificação Hierárquica em Duas Etapas",
                descricao="Primeira etapa identifica o mercado (interno vs externo); segunda etapa classifica o sentimento (positivo, neutro, negativo). Avaliado via validação cruzada.",
                modelo="Pipeline Hierárquico com validação cruzada"
            )
        ],
        preprocessamento=PreprocessamentoInfo(
            regras=[
                "Remoção de títulos duplicados (20 duplicatas removidas)",
                "Limpeza e normalização textual de título, subtítulo e corpo",
                "Separação da coluna 'Classe' em 'mercado' e 'sentimento'",
                "Recuperação dos links originais a partir da base do scraper Canal Rural",
                "Mapeamento de rótulos manuais (611 amostras anotadas à mão) e previsões de modelo",
                "Alinhamento de datas para próximo dia útil de pregão CEPEA (fins de semana e feriados)"
            ],
            colunas_finais=[
                "id",
                "titulo",
                "subtitulo",
                "data",
                "data_dia",
                "data_pregao",
                "texto",
                "link",
                "mercado",
                "sentimento",
                "origem_rotulo"
            ]
        )
    )
