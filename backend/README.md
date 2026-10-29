# Backend — ASAC

API FastAPI e pipeline de banco de dados do projeto ASAC.

## 📁 Estrutura

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analysis.py      # /api/analysis (timeseries, correlation, summary)
│   │   │   ├── health.py        # /api/health
│   │   │   ├── methods.py       # /api/methods
│   │   │   ├── metrics.py       # /api/metrics/model
│   │   │   ├── news.py          # /api/news
│   │   │   ├── prices.py        # /api/prices
│   │   │   └── reports.py       # /api/reports
│   │   └── router.py            # Agregador de rotas com prefixo /api
│   ├── core/
│   │   ├── config.py            # Configurações de ambiente e CORS
│   │   └── database.py          # Conexão e dependência do SQLite
│   ├── schemas/                 # Modelos Pydantic de validação
│   ├── services/
│   │   ├── data_loader.py       # Leitura e limpeza dos CSVs
│   │   └── llm_service.py       # Geração de resumos IA + cache em SQLite
│   ├── tests/
│   │   └── test_api.py          # Testes com TestClient
│   ├── __init__.py
│   └── main.py                  # Ponto de entrada FastAPI com CORS
├── data/
│   ├── cepea-consulta-parana.csv
│   ├── cepea-consulta-paranagua.csv
│   ├── noticias_classificadas_todas.csv
│   ├── noticias_soja_canal_rural.csv
│   └── todas-noticias-e-amostra-classificada.csv
├── build_db.py                  # Gera o banco noticias_cepea.db
├── noticias_cepea.db            # Gerado, não vai pro git (.gitignore)
├── .env.example
├── .env
├── requirements.txt
└── README.md
```

## ⚙️ Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Gerar / Atualizar o Banco de Dados
Lê os CSVs em `data/`, limpa e monta o banco `noticias_cepea.db` do zero (apaga e recria se já existir):
```bash
python build_db.py
```
No final executa um teste de integridade e imprime `integridade ok`.

### 3. Iniciar o servidor da API
```bash
uvicorn app.main:app --reload
```

Documentação interativa disponível em:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Rodar Testes Automatizados
```bash
python -m unittest app/tests/test_api.py
```

---

## 🚀 Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/health` | Status da API e saúde da conexão com o banco SQLite |
| `GET` | `/api/methods` | Estratégias testadas e regras de pré-processamento |
| `GET` | `/api/metrics/model` | Métricas gerais e por classe do modelo de classificação |
| `GET` | `/api/news` | Notícias com paginação (`page`, `page_size`) e filtros |
| `GET` | `/api/prices` | Série histórica de preços CEPEA por praça e datas |
| `GET` | `/api/analysis/timeseries` | Série temporal de Preço × Sentimento (diário ou semanal) |
| `GET` | `/api/analysis/correlation` | Coeficientes por mercado, praça e defasagem (0 a 5 dias) |
| `GET` | `/api/analysis/summary` | Resumo analítico com IA (cache na tabela `resumos`) |
| `GET` | `/api/reports` | Relatório consolidado analítico |

---

## 🤖 Resumos com IA

- O serviço utiliza chave `GEMINI_API_KEY` (opcional no `.env`).
- Caso não haja chave configurada, a API utiliza automaticamente um **template estruturado**.
- Os resumos utilizam apenas números agregados (nunca notícias brutas).
- Há proibição explícita no prompt contra afirmações de causalidade entre sentimento e preço.
- Cada resumo gerado é salvo na tabela `resumos` para cache.

---

## 📊 Dados e Banco de Dados (`noticias_cepea.db`)

**Tabelas:**
- `noticias` — id, titulo, subtitulo, data, data_dia, data_pregao, texto, link, mercado, sentimento, origem_rotulo
- `precos` — data, praca, valor_brl, valor_usd, var_pct
- `metricas_modelo` / `metricas_por_classe` — métricas do modelo de classificação
- `resumos` — cache dos resumos gerados por IA

**Views:**
- `vw_sentimento_diario` — contagem de sentimento por dia de pregão e mercado
- `vw_sentimento_semanal` — contagem de sentimento agregada por semana
- `vw_preco_x_sentimento` — sentimento diário já cruzado com o preço da praça correspondente
`data_pregao` é o próximo dia de pregão CEPEA depois da publicação da notícia — é assim que notícia e preço são cruzados, já que notícia sai todo dia e preço só em dia útil.