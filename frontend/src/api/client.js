const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Falha no healthcheck: ${res.statusText}`);
  return res.json();
}

export async function fetchTimeseries({ frequencia = 'semanal', mercado, data_inicio, data_fim } = {}) {
  const params = new URLSearchParams();
  if (frequencia) params.append('frequencia', frequencia);
  if (mercado && mercado !== 'todos') params.append('mercado', mercado);
  if (data_inicio) params.append('data_inicio', data_inicio);
  if (data_fim) params.append('data_fim', data_fim);

  const res = await fetch(`${API_BASE}/analysis/timeseries?${params.toString()}`);
  if (!res.ok) throw new Error(`Falha ao obter série temporal: ${res.statusText}`);
  return res.json();
}

export async function fetchCorrelation({ mercado, praca } = {}) {
  const params = new URLSearchParams();
  if (mercado && mercado !== 'todos') params.append('mercado', mercado);
  if (praca) params.append('praca', praca);

  const res = await fetch(`${API_BASE}/analysis/correlation?${params.toString()}`);
  if (!res.ok) throw new Error(`Falha ao obter correlações: ${res.statusText}`);
  return res.json();
}

export async function fetchSummary({ periodo = '2023-2026', praca = 'parana' } = {}) {
  const params = new URLSearchParams({ periodo, praca });
  const res = await fetch(`${API_BASE}/analysis/summary?${params.toString()}`);
  if (!res.ok) throw new Error(`Falha ao obter resumo da IA: ${res.statusText}`);
  return res.json();
}

export async function fetchNews({
  page = 1,
  pageSize = 20,
  mercado,
  sentimento,
  origem_rotulo,
  data_inicio,
  data_fim
} = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  if (mercado && mercado !== 'todos') params.append('mercado', mercado);
  if (sentimento && sentimento !== 'todos') params.append('sentimento', sentimento);
  if (origem_rotulo && origem_rotulo !== 'todas') params.append('origem_rotulo', origem_rotulo);
  if (data_inicio) params.append('data_inicio', data_inicio);
  if (data_fim) params.append('data_fim', data_fim);

  const res = await fetch(`${API_BASE}/news?${params.toString()}`);
  if (!res.ok) throw new Error(`Falha ao listar notícias: ${res.statusText}`);
  return res.json();
}

export async function fetchMethods() {
  const res = await fetch(`${API_BASE}/methods`);
  if (!res.ok) throw new Error(`Falha ao carregar métodos: ${res.statusText}`);
  return res.json();
}

export async function fetchModelMetrics() {
  const res = await fetch(`${API_BASE}/metrics/model`);
  if (!res.ok) throw new Error(`Falha ao carregar métricas: ${res.statusText}`);
  return res.json();
}

export async function fetchReport() {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error(`Falha ao carregar relatório: ${res.statusText}`);
  return res.json();
}

