from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API FastAPI para análise de sentimento de notícias e correlação com preços de soja CEPEA.",
    docs_url="/docs",
    redoc_url="/redoc"
)

if "*" in settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API ASAC ativa",
        "docs": "/docs",
        "health": "/api/health"
    }
