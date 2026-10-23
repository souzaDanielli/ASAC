from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class NoticiaBase(BaseModel):
    titulo: str = Field(description="Título da notícia")
    subtitulo: Optional[str] = Field(default=None, description="Subtítulo ou resumo da notícia")
    data: str = Field(description="Data e hora de publicação")
    data_dia: Optional[str] = Field(default=None, description="Data normalizada (YYYY-MM-DD)")
    data_pregao: Optional[str] = Field(default=None, description="Data do pregão associado")
    texto: str = Field(description="Corpo/conteúdo da notícia")
    link: Optional[str] = Field(default=None, description="Link original da notícia")
    mercado: Optional[str] = Field(default=None, description="Mercado (interno ou externo)")
    sentimento: Optional[str] = Field(default=None, description="Sentimento (positivo, negativo, neutro)")
    origem_rotulo: Optional[str] = Field(default=None, description="Origem da classificação (modelo, manual)")

class NoticiaCreate(NoticiaBase):
    pass

class NoticiaResponse(NoticiaBase):
    id: Optional[int] = Field(default=None, description="Identificador no banco de dados")

    model_config = ConfigDict(from_attributes=True)
