# ASAC - Backend API (FastAPI)

Estrutura base do projeto FastAPI.

## 📁 Estrutura

```text
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analise.py
│   │   ├── cotacao.py
│   │   ├── metrica.py
│   │   ├── noticia.py
│   │   ├── preco.py
│   │   └── resumo.py
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── cepea-consulta-parana.csv
│   ├── cepea-consulta-paranagua.csv
│   └── noticias_classificadas_todas.csv
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Como Executar

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Iniciar o servidor** (a partir da pasta `backend`):
```bash
uvicorn app.main:app --reload
```

A documentação interativa fica disponível em:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
