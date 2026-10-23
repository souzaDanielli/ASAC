from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class MetricaModeloBase(BaseModel):
    nome_modelo: str = Field(description="Nome ou identificador do modelo")
    acuracia: Optional[float] = None
    f1_score: Optional[float] = None
    precisao: Optional[float] = None
    recall: Optional[float] = None
    data_avaliacao: Optional[str] = None

class MetricaModeloResponse(MetricaModeloBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class MetricaPorClasseBase(BaseModel):
    classe: str = Field(description="Nome da classe (ex: mercado interno positivo)")
    precisao: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    suporte: Optional[int] = None

class MetricaPorClasseResponse(MetricaPorClasseBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
