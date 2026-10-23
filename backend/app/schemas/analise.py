from typing import Optional
from pydantic import BaseModel, ConfigDict

class SentimentoDiarioResponse(BaseModel):
    data_dia: str
    total_noticias: int
    positivos: int
    negativos: int
    neutros: int
    score_sentimento: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class SentimentoSemanalResponse(BaseModel):
    semana: str
    total_noticias: int
    positivos: int
    negativos: int
    neutros: int
    score_sentimento: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class PrecoXSentimentoResponse(BaseModel):
    data: str
    praca: str
    valor_brl: float
    var_pct: Optional[float] = None
    sentimento_predominante: Optional[str] = None
    score_sentimento: Optional[float] = None
    total_noticias: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
