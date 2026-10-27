# Backend — ASAC

API FastAPI e pipeline de banco de dados do projeto ASAC.

## 📁 Estrutura

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── schemas/
│   ├── services/
│   │   └── data_loader.py   # Leitura e limpeza dos CSVs
│   ├── tests/
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── cepea-consulta-parana.csv
│   ├── cepea-consulta-paranagua.csv
│   ├── noticias_classificadas_todas.csv
│   ├── noticias_soja_canal_rural.csv
│   └── todas-noticias-e-amostra-classificada.csv
├── build_db.py              # Gera o banco noticias_cepea.db
├── noticias_cepea.db        # Gerado, não vai pro git (.gitignore)
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

## 📊 Dados

- `noticias_classificadas_todas.csv` — 6.340 linhas brutas, 20 títulos duplicados (6.320 válidas depois da limpeza). Coluna `Classe` no formato `"mercado <interno|externo> <positivo|neutro|negativo>"`.
- `noticias_soja_canal_rural.csv` — CSV bruto do scraper, usado só pra recuperar a coluna `Link`.
- `todas-noticias-e-amostra-classificada.csv` — usado pra marcar quais notícias foram rotuladas à mão (611) e quais pelo modelo.
- `cepea-consulta-parana.csv` / `cepea-consulta-paranagua.csv` — 1.417 pregões cada. Paraná = mercado interno, Paranaguá = preço no porto (exportação).

## 🗄️ Banco de Dados (`noticias_cepea.db`)

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
