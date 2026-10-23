from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PrecoBase(BaseModel):
    data: str = Field(description="Data da cotação")
    praca: str = Field(description="Praça/Região (ex: Paraná, Paranaguá)")
    valor_brl: float = Field(description="Valor em Reais (R$)")
    valor_usd: Optional[float] = Field(default=None, description="Valor em Dólares (US$)")
    var_pct: Optional[float] = Field(default=None, description="Variação percentual diária")

class PrecoCreate(PrecoBase):
    pass

class PrecoResponse(PrecoBase):
    id: Optional[int] = Field(default=None, description="Identificador no banco de dados")

    model_config = ConfigDict(from_attributes=True)
