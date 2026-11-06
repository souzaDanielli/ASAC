# Frontend — ASAC

Interface moderna, limpa e responsiva em **React**, **Vite** e **Tailwind CSS** para o projeto ASAC (Análise de Sentimento do Agronegócio e Preços CEPEA), desenvolvida fielmente a partir do mockup.

## 🚀 Como Executar

### 1. Instalar as dependências
```bash
npm install
```

### 2. Iniciar o servidor de desenvolvimento
```bash
npm run dev
```

A aplicação estará disponível em [http://localhost:5173](http://localhost:5173).

### 3. Compilar para produção
```bash
npm run build
```

---

## 📁 Estrutura de Pastas

```text
frontend/
├── src/
│   ├── api/
│   │   └── client.js            # Cliente HTTP centralizado para consumo da API FastAPI
│   ├── components/
│   │   ├── Header.jsx           # Cabeçalho institucional e navegação entre abas
│   │   ├── OverviewTab.jsx      # Aba 1: KPIs, Série Temporal, Correlação e Resumo IA
│   │   ├── NewsTab.jsx          # Aba 2: Listagem paginada de notícias, filtros e modal
│   │   ├── MethodsTab.jsx       # Aba 3: Pipeline metodológico e métricas de ML
│   │   └── ReportsTab.jsx       # Aba 4: Relatório executivo consolidado e exportação PDF
│   ├── App.jsx                  # Gerenciamento de estado global da aba ativa
│   ├── main.jsx                 # Ponto de entrada React
│   └── index.css                # Diretivas Tailwind CSS e estilos de impressão (@media print)
├── .env.example
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```

---

## 🎨 Estrutura das Abas e Componentes

1. **Visão geral (`OverviewTab.jsx`)**
   - 4 Cartões KPI: Notícias (6.320), Pregões (1.417), Período e Acurácia do Modelo.
   - Gráfico de Linha Interativo com 2 Eixos Y: Preço CEPEA (R$/saca em ocre) e Índice de Sentimento (linha tracejada escura).
   - Filtros dinâmicos: Frequência (Semanal/Diário), Mercado (Todos/Interno/Externo) e Intervalo de Datas.
   - Cartões inferiores lado a lado:
     - Gráfico de barras agrupadas de Correlação de Pearson por defasagem (t+0 a t+5) para Paraná e Paranaguá.
     - Resumo gerado por IA (Gemini) com cache e notas sobre causalidade.

2. **Notícias (`NewsTab.jsx`)**
   - Listagem paginada de todas as notícias com filtros por Mercado, Sentimento, Origem do Rótulo e Período.
   - Badges estilizados de sentimento (positivo em verde, negativo em vermelho, neutro em cinza).
   - Modal com visualização completa do texto da notícia, metadados e link original para o Canal Rural.

3. **Metodologia e métricas (`MethodsTab.jsx`)**
   - 4 Cartões numerados detalhando as etapas do pipeline.
   - Métricas de assertividade (Acurácia, Precisão, Recall e F1-score).
   - Tabela comparativa das estratégias de Machine Learning avaliadas (Validação Cruzada vs Pseudo-labeling) e métricas detalhadas por classe.

4. **Relatório (`ReportsTab.jsx`)**
   - Visão consolidada para exportação e impressão em PDF (com suporte a `@media print`).
   - Resumo geral, gráficos consolidados e lista estruturada de insights principais.

