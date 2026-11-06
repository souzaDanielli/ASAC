import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db


def _broken_db():
    class BrokenConnection:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Falha simulada no banco de dados")
    yield BrokenConnection()


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides.clear()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    # --- 1. Root (/) ---
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["status"] if "status" in data else data["message"], "API ASAC ativa")

    def test_root_error_method_not_allowed(self):
        response = self.client.post("/")
        self.assertEqual(response.status_code, 405)

    # --- 2. Health (/api/health) ---
    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["database_status"], "connected")
        self.assertEqual(data["total_noticias"], 6320)
        self.assertEqual(data["total_precos"], 2834)  # 1417 * 2

    def test_health_error_db_failure(self):
        app.dependency_overrides[get_db] = _broken_db
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())

    # --- 3. Methods (/api/methods) ---
    def test_methods(self):
        response = self.client.get("/api/methods")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("estrategias_testadas", data)
        self.assertIn("preprocessamento", data)
        self.assertGreater(len(data["estrategias_testadas"]), 0)

    def test_methods_error_method_not_allowed(self):
        response = self.client.post("/api/methods")
        self.assertEqual(response.status_code, 405)

    # --- 4. Metrics (/api/metrics/model) ---
    def test_metrics_model(self):
        response = self.client.get("/api/metrics/model")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("estrategia_padrao", data)
        self.assertIn("metricas_gerais", data)
        self.assertIn("metricas_por_classe", data)

    def test_metrics_model_error_db_failure(self):
        app.dependency_overrides[get_db] = _broken_db
        response = self.client.get("/api/metrics/model")
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())

    # --- 5. News (/api/news) ---
    def test_news_pagination(self):
        response = self.client.get("/api/news?page=1&page_size=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 5)
        self.assertEqual(len(data["items"]), 5)
        self.assertEqual(data["total"], 6320)

    def test_news_filters(self):
        response = self.client.get("/api/news?mercado=interno&sentimento=positivo&page_size=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for item in data["items"]:
            self.assertEqual(item["mercado"].lower(), "interno")
            self.assertEqual(item["sentimento"].lower(), "positivo")

    def test_news_invalid_page(self):
        response = self.client.get("/api/news?page=0")
        self.assertEqual(response.status_code, 422)  # Validação Pydantic/FastAPI

    def test_news_invalid_filters(self):
        self.assertEqual(self.client.get("/api/news?mercado=invalido").status_code, 422)
        self.assertEqual(self.client.get("/api/news?sentimento=invalido").status_code, 422)
        self.assertEqual(self.client.get("/api/news?data_inicio=2026/01/01").status_code, 422)
        self.assertEqual(self.client.get("/api/news?data_inicio=2026-09-01&data_fim=2026-01-01").status_code, 400)

    # --- 6. Prices (/api/prices) ---
    def test_prices(self):
        response = self.client.get("/api/prices?praca=parana&limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data), 10)
        for item in data:
            self.assertEqual(item["praca"].lower(), "parana")
            self.assertIn("valor_brl", item)

    def test_prices_invalid_params(self):
        self.assertEqual(self.client.get("/api/prices?limit=0").status_code, 422)
        self.assertEqual(self.client.get("/api/prices?limit=5001").status_code, 422)
        self.assertEqual(self.client.get("/api/prices?praca=santos").status_code, 422)
        self.assertEqual(self.client.get("/api/prices?data_inicio=2026-09-01&data_fim=2026-01-01").status_code, 400)

    # --- 7. Timeseries (/api/analysis/timeseries) ---
    def test_timeseries_diario(self):
        response = self.client.get("/api/analysis/timeseries?frequencia=diario")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_timeseries_semanal(self):
        response = self.client.get("/api/analysis/timeseries?frequencia=semanal")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_timeseries_invalid_frequency(self):
        response = self.client.get("/api/analysis/timeseries?frequencia=mensal")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/api/analysis/timeseries?mercado=invalido").status_code, 422)
        self.assertEqual(self.client.get("/api/analysis/timeseries?data_inicio=2026-09-01&data_fim=2026-01-01").status_code, 400)

    # --- 8. Correlation (/api/analysis/correlation) ---
    def test_correlation(self):
        response = self.client.get("/api/analysis/correlation")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("resultados", data)
        self.assertEqual(len(data["resultados"]), 12)  # 2 praças x 6 lags (0 a 5)

    def test_correlation_invalid_params(self):
        self.assertEqual(self.client.get("/api/analysis/correlation?mercado=invalido").status_code, 422)
        self.assertEqual(self.client.get("/api/analysis/correlation?praca=santos").status_code, 422)

    # --- 9. Summary (/api/analysis/summary) ---
    def test_summary_and_cache(self):
        # 1a chamada gera e salva em cache
        response = self.client.get("/api/analysis/summary?periodo=teste_ci&praca=parana")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("texto", data)
        texto_lower = data["texto"].lower()
        self.assertTrue("causalidade" in texto_lower or "inferir" in texto_lower)

        # 2a chamada recupera do cache
        response_cache = self.client.get("/api/analysis/summary?periodo=teste_ci&praca=parana")
        self.assertEqual(response_cache.status_code, 200)
        data_cache = response_cache.json()
        self.assertEqual(data_cache["fonte"], "cache")

    def test_summary_invalid_params(self):
        self.assertEqual(self.client.get("/api/analysis/summary?praca=santos").status_code, 422)
        self.assertEqual(self.client.get("/api/analysis/summary?periodo=").status_code, 422)

    # --- 10. Reports (/api/reports) ---
    def test_reports(self):
        response = self.client.get("/api/reports")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("titulo", data)
        self.assertEqual(data["total_noticias"], 6320)
        self.assertIn("insights_principais", data)

    def test_reports_error_db_failure(self):
        app.dependency_overrides[get_db] = _broken_db
        response = self.client.get("/api/reports")
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())

    # --- 11. Chart Timeseries (/api/reports/chart/timeseries) ---
    def test_chart_timeseries(self):
        response = self.client.get("/api/reports/chart/timeseries")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG"))

    def test_chart_timeseries_error_db_failure(self):
        app.dependency_overrides[get_db] = _broken_db
        response = self.client.get("/api/reports/chart/timeseries")
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())

    # --- 12. Chart Correlation (/api/reports/chart/correlation) ---
    def test_chart_correlation(self):
        response = self.client.get("/api/reports/chart/correlation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG"))

    def test_chart_correlation_error(self):
        with patch("app.api.routes.charts.grafico_correlacao", side_effect=RuntimeError("Erro simulado no gráfico")):
            response = self.client.get("/api/reports/chart/correlation")
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.json())


if __name__ == "__main__":
    unittest.main()
