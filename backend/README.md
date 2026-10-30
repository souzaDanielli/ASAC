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
│   │   │   ├── reports.py       # /api/reports
│   │   │   └── charts.py        # /api/reports/chart (gráficos PNG gerados na hora)
│   │   └── router.py            # Agregador de rotas com prefixo /api
│   ├── core/
│   │   ├── config.py            # Configurações de ambiente e CORS
│   │   └── database.py          # Conexão e dependência do SQLite
│   ├── schemas/                 # Modelos Pydantic de validação
│   ├── services/
│   │   ├── data_loader.py       # Leitura e limpeza dos CSVs
│   │   ├── analise.py           # Correlação sentimento x preço (Pearson/Spearman)
│   │   ├── metricas_modelo.py   # Reavaliação da Estratégia 2 (CV e pseudo-label)
│   │   ├── graficos.py          # Geração dos gráficos (matplotlib)
│   │   ├── relatorio.py         # Monta o PDF consumindo as próprias rotas da API
│   │   └── llm_service.py       # Geração de resumos IA + cache em SQLite
│   ├── tests/
│   │   ├── test_api.py          # Testes com TestClient
│   │   ├── test_data_loader.py  # Testes de leitura e limpeza dos dados
│   │   └── test_analise.py      # Testes do cálculo de correlação
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

### 1. Criar e ativar o ambiente virtual
```bash
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
Linux/Mac:
```bash
source .venv/bin/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Gerar / Atualizar o Banco de Dados
Lê os CSVs em `data/`, limpa e monta o banco `noticias_cepea.db` do zero (apaga e recria se já existir):
```bash
python build_db.py
```
No final executa um teste de integridade e imprime `integridade ok`.

### 4. Iniciar o servidor da API
```bash
uvicorn app.main:app --reload
```

Documentação interativa disponível em:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Rodar Testes Automatizados
```bash
python -m pytest app/tests/ -v
```
Cobre os testes da API (`test_api.py`), da leitura/limpeza dos dados (`test_data_loader.py`) e do cálculo de correlação (`test_analise.py`).

### 6. Reavaliar as métricas do modelo
Recalcula a acurácia da Estratégia 2 (validação cruzada e pseudo-labeling do léxico) e grava em `metricas_modelo` / `metricas_por_classe`:
```bash
python app/services/metricas_modelo.py
```

### 7. Gerar o relatório em PDF
Com a API rodando (passo 4), monta um PDF consumindo as próprias rotas (`/api/reports`, `/api/analysis/summary`, `/api/reports/chart/*`):
```bash
python -m app.services.relatorio
```
Gera `relatorio_asac.pdf` na pasta `backend/`.

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
| `GET` | `/api/reports/chart/timeseries` | Gráfico (PNG) de série temporal sentimento x preço |
| `GET` | `/api/reports/chart/correlation` | Gráfico (PNG) de correlação por defasagem |

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

---

## 📈 Métricas do modelo de classificação

A acurácia originalmente reportada para a Estratégia 2 (TF-IDF + ML Otimizado, 59%) foi calculada
avaliando o modelo nos mesmos dados em que foi treinado — um vazamento que infla o resultado.
`metricas_modelo.py` reavalia a Estratégia 2 de duas formas, sem esse vazamento, e grava as duas no banco:

- **Validação cruzada (5-fold)**: TF-IDF no título treinado direto com `Análise Manual`, avaliado com
  `StratifiedKFold`.
- **Pseudo-labeling**: réplica do desenho original da estratégia — treina com os pseudo-rótulos do
  léxico (Estratégia 1) em cima do texto completo (~5.700 notícias), e testa nas 611 notícias com
  rótulo manual, que o modelo nunca viu durante o treino.

Os dois resultados ficam em `metricas_modelo` (acurácia/F1 geral) e `metricas_por_classe` (detalhado
por classe), disponíveis via `GET /api/metrics/model`.