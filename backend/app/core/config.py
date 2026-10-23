import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    PROJECT_NAME: str = "ASAC - API de Análise de Sentimento de Notícias e Correlação com Preços"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API FastAPI para o projeto ASAC."
    API_V1_STR: str = "/api/v1"

    HOST: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default=int(os.getenv("PORT", "8000")))

    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:3000,http://127.0.0.1:8080,*"
            ).split(",")
            if origin.strip()
        ]
    )

settings = Settings()
