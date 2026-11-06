# ASAC — Análise de Sentimento do Agronegócio e Correlação com Preços CEPEA

Plataforma full-stack para coleta, classificação de sentimento de notícias do setor da soja (Canal Rural) e análise estatística de correlação com o indicador de preços **CEPEA/ESALQ** (mercado interno no **Paraná** e mercado externo no porto de **Paranaguá**).

---

## 🏛️ Arquitetura do Projeto

O sistema é dividido em dois módulos independentes que se comunicam via API REST JSON:

```text
ASAC/
├── backend/                 # API FastAPI, banco SQLite, pipeline de ML/estatística e testes
│   ├── app/
│   │   ├── api/routes/      # Endpoints REST (/health, /methods, /metrics, /news, /prices, /analysis, /reports)
│   │   ├── core/            # Configurações (.env, CORS) e conexão SQLite (WAL mode)
│   │   ├── schemas/         # Contratos de entrada/saída validados com Pydantic v2
│   │   ├── services/        # Regras de negócio (limpeza CSV, correlação, ML, LLM com cache, gráficos e PDF)
│   │   └── tests/           # Suíte automatizada de testes unitários e de integração (27 testes de API + serviços)
│   ├── data/                # Bases CSV brutas e classificadas (notícias Canal Rural e cotações CEPEA)
│   ├── build_db.py          # Script ETL que constrói e valida o banco SQLite (noticias_cepea.db)
│   └── requirements.txt     # Dependências Python do projeto
└── frontend/                # SPA em React 18, Vite, Tailwind CSS e Recharts
    └── src/
        ├── api/             # Cliente HTTP para integração com o backend
        └── components/      # Abas: Visão Geral, Notícias, Metodologia & Métricas, e Relatório
```

---

## ⚙️ Como Executar o Projeto Completo

### Pré-requisitos
- **Python 3.10+**
- **Node.js 18+** e **npm**

### 1. Rodar o Backend (API FastAPI)

```bash
cd backend

# 1. (Opcional) Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

# 2. Instalar todas as dependências
pip install -r requirements.txt

# 3. Construir o banco SQLite a partir dos CSVs (caso ainda não exista)
python build_db.py

# 4. (Opcional) Recalcular e gravar as métricas do modelo de ML no banco
python app/services/metricas_modelo.py

# 5. Iniciar o servidor FastAPI na porta 8000
uvicorn app.main:app --reload
```

- **API Base**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI (Documentação Interativa)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Rodar o Frontend (React + Vite)

Em outro terminal:

```bash
cd frontend

# 1. Instalar dependências Node
npm install

# 2. Iniciar servidor de desenvolvimento
npm run dev
```

- **Interface Web**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Como Executar os Testes Automatizados

Na pasta `backend/`, você pode rodar toda a suíte (testes de sucesso e erro de todos os endpoints da API, validação de dados e cálculo de correlações):

```bash
cd backend

# Usando pytest (roda test_api.py, test_data_loader.py e test_analise.py)
python -m pytest app/tests/ -v

# Ou usando unittest nativo do Python (roda os 27 testes de endpoints da API)
python -m unittest app/tests/test_api.py -v
```

---

## 📚 Documentação Detalhada por Módulo

- [Documentação do Backend (`backend/README.md`)](./backend/README.md) — detalhes de todas as rotas, tabelas/views SQLite, reavaliação de métricas de Machine Learning e geração de PDF.
- [Documentação do Frontend (`frontend/README.md`)](./frontend/README.md) — detalhes das abas, gráficos interativos e componentes visuais.
