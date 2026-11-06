import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

function getSentimentMeta(score) {
  if (score === null || score === undefined) return null;
  const num = Number(score);
  if (num > 0.3) {
    return {
      text: 'Fortemente Otimista',
      badgeClass: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      dotColor: 'bg-emerald-600',
    };
  }
  if (num > 0.05) {
    return {
      text: 'Otimista',
      badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      dotColor: 'bg-emerald-500',
    };
  }
  if (num < -0.3) {
    return {
      text: 'Fortemente Pessimista',
      badgeClass: 'bg-rose-100 text-rose-800 border-rose-300',
      dotColor: 'bg-rose-600',
    };
  }
  if (num < -0.05) {
    return {
      text: 'Pessimista',
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
      dotColor: 'bg-rose-500',
    };
  }
  return {
    text: 'Neutro / Equilibrado',
    badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
    dotColor: 'bg-slate-400',
  };
}

function formatDateStr(iso) {
  if (!iso) return '';
  const parts = iso.split('-');
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  return iso;
}

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    const preco = dataPoint.valor_brl;
    const sentimento = dataPoint.indice_sentimento;
    const sentMeta = getSentimentMeta(sentimento);

    const isSemanal = !!dataPoint.semana || (dataPoint.semana_inicio && dataPoint.semana_fim);
    const dateTitle = isSemanal && dataPoint.semana_inicio && dataPoint.semana_fim
      ? `Semana: ${formatDateStr(dataPoint.semana_inicio)} a ${formatDateStr(dataPoint.semana_fim)}`
      : dataPoint.formattedDate || label;

    const pracaLabel =
      dataPoint.mercado === 'interno'
        ? 'Paraná (Disponível)'
        : dataPoint.mercado === 'externo'
        ? 'Paranaguá (Porto)'
        : 'Média (PR + Paranaguá)';

    const precoTipo = isSemanal ? 'Média Semanal' : 'Fechamento Diário';

    return (
      <div className="bg-white/95 backdrop-blur-sm p-3.5 border border-slate-200 rounded-lg shadow-lg text-xs space-y-2 min-w-[230px]">
        {/* Header: Date + Market tag */}
        <div className="font-semibold text-slate-700 pb-1.5 border-b border-slate-100 flex justify-between items-center gap-2">
          <span className="font-mono">{dateTitle}</span>
          <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded whitespace-nowrap">
            {pracaLabel}
          </span>
        </div>

        {/* Preço CEPEA com indicação de tipo */}
        {preco !== null && preco !== undefined && (
          <div className="flex items-center justify-between text-[#b45309]">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2.5 h-0.5 bg-[#d97706] inline-block" />
              Preço ({precoTipo}):
            </span>
            <span className="font-bold font-mono text-sm">
              {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2 }).format(preco)}
            </span>
          </div>
        )}

        {/* Índice de Sentimento Numérico + Etiqueta Qualitativa */}
        {sentimento !== null && sentimento !== undefined && (
          <div className="space-y-1 pt-0.5 border-t border-slate-50">
            <div className="flex items-center justify-between text-[#1e293b]">
              <span className="flex items-center gap-1.5 font-medium">
                <span className="w-2.5 h-0.5 border-t border-dashed border-[#1e293b] inline-block" />
                Índice Sentimento:
              </span>
              <span className="font-bold font-mono">
                {Number(sentimento) > 0 ? `+${Number(sentimento).toFixed(4)}` : Number(sentimento).toFixed(4)}
              </span>
            </div>

            {/* Etiqueta visual de interpretação */}
            {sentMeta && (
              <div className="flex justify-end pt-0.5">
                <span
                  className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium border ${sentMeta.badgeClass}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${sentMeta.dotColor}`} />
                  {sentMeta.text}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Notícias no Período */}
        {dataPoint.qtd_total !== undefined && (
          <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-100 flex justify-between">
            <span>Amostra de notícias:</span>
            <span className="font-semibold text-slate-600">{dataPoint.qtd_total}</span>
          </div>
        )}
      </div>
    );
  }
  return null;
}

export default function PriceSentimentChart({ data = [], loading = false }) {
  if (loading) {
    return (
      <div className="h-72 w-full flex items-center justify-center bg-slate-50/50 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-6 h-6 border-2 border-[#1a3c34] border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-slate-400">Carregando dados da série...</span>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-72 w-full flex items-center justify-center bg-slate-50/50 rounded-lg text-xs text-slate-400">
        Nenhum dado encontrado para o filtro selecionado.
      </div>
    );
  }

  // Pre-process dates for display
  const chartData = data.map((item) => {
    const rawDate = item.data || item.semana_inicio || item.semana || '';
    let displayLabel = rawDate;
    if (rawDate.includes('-')) {
      const parts = rawDate.split('-');
      if (parts.length >= 3) {
        displayLabel = `${parts[2]}/${parts[1]}/${parts[0].slice(2)}`;
      } else if (parts.length === 2) {
        displayLabel = `${parts[1]}/${parts[0].slice(2)}`;
      }
    }
    return {
      ...item,
      label: displayLabel,
      formattedDate: rawDate,
      valor_brl: item.valor_brl != null ? Number(item.valor_brl) : null,
      indice_sentimento: item.indice_sentimento != null ? Number(item.indice_sentimento) : null,
    };
  });

  return (
    <div className="w-full">
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 12, right: 15, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
            <XAxis
              dataKey="label"
              tickLine={false}
              axisLine={{ stroke: '#CBD5E1' }}
              tick={{ fill: '#64748B', fontSize: 11 }}
              minTickGap={40}
            />
            {/* Left Y-Axis for Price (R$/saca) com 2 casas decimais quando apropriado */}
            <YAxis
              yAxisId="preco"
              orientation="left"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#b45309', fontSize: 11, fontWeight: 500 }}
              tickFormatter={(v) => `R$ ${Math.round(v)}`}
              domain={[(dataMin) => Math.floor(dataMin * 0.96), (dataMax) => Math.ceil(dataMax * 1.04)]}
            />
            {/* Right Y-Axis for Sentiment Index */}
            <YAxis
              yAxisId="sentimento"
              orientation="right"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#1e293b', fontSize: 11 }}
              tickFormatter={(v) => Number(v).toFixed(1)}
              domain={[-0.8, 0.8]}
            />
            <Tooltip content={<CustomTooltip />} />
            {/* Golden Ochre / Yellow Line for Preço */}
            <Line
              yAxisId="preco"
              type="monotone"
              dataKey="valor_brl"
              name="Preço (R$/saca)"
              stroke="#d97706"
              strokeWidth={2.8}
              dot={false}
              activeDot={{ r: 5, stroke: '#d97706', fill: '#fff', strokeWidth: 2.5 }}
              connectNulls
            />
            {/* Dark Slate Dashed Line for Índice de Sentimento */}
            <Line
              yAxisId="sentimento"
              type="monotone"
              dataKey="indice_sentimento"
              name="Índice de sentimento"
              stroke="#1e293b"
              strokeWidth={1.8}
              strokeDasharray="4 4"
              dot={false}
              activeDot={{ r: 4, stroke: '#1e293b', fill: '#fff', strokeWidth: 2 }}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Mockup styled legend with praça indicator */}
      <div className="flex flex-wrap items-center justify-between gap-4 mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <span className="w-5 h-0.5 bg-[#d97706] inline-block rounded" />
            <span className="font-semibold text-slate-700">━ Preço (R$/saca)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-5 h-0.5 border-t-2 border-dashed border-[#1e293b] inline-block" />
            <span className="font-semibold text-slate-700">┅ Índice de sentimento</span>
          </div>
        </div>

        {/* Aviso de Praças de Referência */}
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-50 border border-slate-200/80 text-[11px] text-slate-500 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
          <span>Praças: <strong>Interno = Paraná</strong> · <strong>Externo = Paranaguá</strong> · <strong>Todos = Média</strong></span>
        </div>
      </div>
    </div>
  );
}
