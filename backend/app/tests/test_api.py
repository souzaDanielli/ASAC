import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["status"] if "status" in data else data["message"], "API ASAC ativa")

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["database_status"], "connected")
        self.assertEqual(data["total_noticias"], 6320)
        self.assertEqual(data["total_precos"], 2834)  # 1417 * 2

    def test_methods(self):
        response = self.client.get("/api/methods")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("estrategias_testadas", data)
        self.assertIn("preprocessamento", data)
        self.assertGreater(len(data["estrategias_testadas"]), 0)

    def test_metrics_model(self):
        response = self.client.get("/api/metrics/model")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("estrategia_padrao", data)
        self.assertIn("metricas_gerais", data)
        self.assertIn("metricas_por_classe", data)

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

    def test_prices(self):
        response = self.client.get("/api/prices?praca=parana&limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data), 10)
        for item in data:
            self.assertEqual(item["praca"].lower(), "parana")
            self.assertIn("valor_brl", item)

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

    def test_correlation(self):
        response = self.client.get("/api/analysis/correlation")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("resultados", data)
        self.assertEqual(len(data["resultados"]), 12)  # 2 praças x 6 lags (0 a 5)

    def test_summary_and_cache(self):
        # 1a chamada gera e salva em cache
        response = self.client.get("/api/analysis/summary?periodo=teste_ci&praca=parana")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("texto", data)
        self.assertIn("inferir que o sentimento das", data["texto"].lower())

        # 2a chamada recupera do cache
        response_cache = self.client.get("/api/analysis/summary?periodo=teste_ci&praca=parana")
        self.assertEqual(response_cache.status_code, 200)
        data_cache = response_cache.json()
        self.assertEqual(data_cache["fonte"], "cache")

    def test_reports(self):
        response = self.client.get("/api/reports")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("titulo", data)
        self.assertEqual(data["total_noticias"], 6320)
        self.assertIn("insights_principais", data)

if __name__ == "__main__":
    unittest.main()
