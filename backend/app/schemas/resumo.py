from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ResumoBase(BaseModel):
    data_referencia: Optional[str] = Field(default=None, description="Data de referência")
    tipo: Optional[str] = Field(default=None, description="Tipo do resumo (ex: diario, semanal)")
    conteudo: str = Field(description="Texto gerado pela IA")

class ResumoCreate(ResumoBase):
    pass

class ResumoResponse(ResumoBase):
    id: Optional[int] = None
    criado_em: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
