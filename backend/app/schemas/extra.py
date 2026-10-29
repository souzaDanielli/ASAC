from typing import List, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(description="Status geral da API (ex: healthy, ok)")
    database_status: str = Field(description="Status da conexão com o banco SQLite")
    total_noticias: int = Field(description="Quantidade de notícias no banco")
    total_precos: int = Field(description="Quantidade de registros de preços no banco")

class PreprocessamentoInfo(BaseModel):
    regras: List[str]
    colunas_finais: List[str]

class EstrategiaInfo(BaseModel):
    id: str
    nome: str
    descricao: str
    modelo: str

class MethodsResponse(BaseModel):
    estrategias_testadas: List[EstrategiaInfo]
    preprocessamento: PreprocessamentoInfo

class PaginatedNewsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[dict]

class CorrelationItem(BaseModel):
    mercado: str
    praca: str
    defasagem_dias: int
    pearson: Optional[float] = None
    spearman: Optional[float] = None
    amostras: Optional[int] = None
    p_valor_pearson: Optional[float] = None
    p_valor_spearman: Optional[float] = None

class CorrelationResponse(BaseModel):
    status: str
    descricao: str
    resultados: List[CorrelationItem]

class ReportResponse(BaseModel):
    titulo: str
    gerado_em: str
    resumo_geral: str
    total_noticias: int
    total_pregoes: int
    periodo_dados: dict
    metricas_modelo: List[dict]
    insights_principais: List[str]
