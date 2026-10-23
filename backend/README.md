# Backend — ASAC


## Estrutura

```
backend/
  app/
    services/
      data_loader.py   # leitura e limpeza dos CSVs
  data/
    noticias_classificadas_todas.csv
    noticias_soja_canal_rural.csv
    todas-noticias-e-amostra-classificada.csv
    cepea-consulta-parana.csv
    cepea-consulta-paranagua.csv
  build_db.py            # gera o banco noticias_cepea.db
  noticias_cepea.db       # gerado, não vai pro git (.gitignore)
```

## Como rodar

```
cd backend
python build_db.py
```

Isso lê os CSVs em `data/`, limpa e monta o banco `noticias_cepea.db` do zero (apaga e recria se já existir). No final roda um teste de integridade e imprime `integridade ok`.

## Dados

- `noticias_classificadas_todas.csv` — 6.340 linhas brutas, 20 títulos duplicados (6.320 válidas depois da limpeza). Coluna `Classe` no formato `"mercado <interno|externo> <positivo|neutro|negativo>"`.
- `noticias_soja_canal_rural.csv` — CSV bruto do scraper, usado só pra recuperar a coluna `Link`.
- `todas-noticias-e-amostra-classificada.csv` — usado pra marcar quais notícias foram rotuladas à mão (611) e quais pelo modelo.
- `cepea-consulta-parana.csv` / `cepea-consulta-paranagua.csv` — 1.417 pregões cada. Paraná = mercado interno, Paranaguá = preço no porto (exportação).

## Banco (`noticias_cepea.db`)

Tabelas:
- `noticias` — id, titulo, subtitulo, data, data_dia, data_pregao, texto, link, mercado, sentimento, origem_rotulo
- `precos` — data, praca, valor_brl, valor_usd, var_pct
- `metricas_modelo` / `metricas_por_classe` — métricas do modelo de classificação (usar os números de validação cruzada, não os do pipeline original — ver `CLAUDE.md`)
- `resumos` — cache dos resumos gerados por IA (gravado pela Pessoa B)

Views:
- `vw_sentimento_diario` — contagem de sentimento por dia de pregão e mercado
- `vw_sentimento_semanal` — mesma coisa, agregado por semana
- `vw_preco_x_sentimento` — sentimento diário já cruzado com o preço da praça correspondente

`data_pregao` é o próximo dia de pregão CEPEA depois da publicação da notícia — é assim que notícia e preço são cruzados, já que notícia sai todo dia e preço só em dia útil.

