from fastapi import APIRouter
from app.api.routes import health, methods, metrics, news, prices, analysis, reports, charts

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(methods.router)
api_router.include_router(metrics.router)
api_router.include_router(news.router)
api_router.include_router(prices.router)
api_router.include_router(analysis.router)
api_router.include_router(reports.router)
api_router.include_router(charts.router)
