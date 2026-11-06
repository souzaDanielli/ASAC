import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';

const LAG_EXPLANATIONS = {
  't+0': 'No mesmo dia em que a notícia saiu',
  't+1': '1 dia após a publicação da notícia',
  't+2': '2 dias após a notícia (Pico de Maior Reação)',
  't+3': '3 dias após a publicação da notícia',
  't+4': '4 dias após a publicação da notícia',
  't+5': '5 dias após a publicação da notícia',
};

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const subtitle = LAG_EXPLANATIONS[label] || '';
    const isPeak = label === 't+2';

    return (
      <div className="bg-white/95 backdrop-blur-sm p-3.5 border border-slate-200 rounded-lg shadow-lg text-xs space-y-2 min-w-[210px]">
        <div className="pb-1.5 border-b border-slate-100">
          <div className="flex items-center justify-between gap-2">
            <span className="font-bold text-slate-800 font-mono text-sm">{label}</span>
            {isPeak && (
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Pico estatístico
              </span>
            )}
          </div>
          <span className="text-[11px] text-slate-500 block mt-0.5 font-medium">{subtitle}</span>
        </div>

        <div className="space-y-1">
          {payload.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between gap-4">
              <span className="flex items-center gap-1.5" style={{ color: item.color }}>
                <span className="w-2.5 h-2.5 rounded-xs" style={{ backgroundColor: item.color }} />
                <span className="font-medium">{item.name}:</span>
              </span>
              <span className="font-mono font-bold text-slate-800">
                {item.value != null ? (item.value > 0 ? `+${Number(item.value).toFixed(4)}` : Number(item.value).toFixed(4)) : 'N/D'}
              </span>
            </div>
          ))}
        </div>

        <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-50 leading-tight">
          Quanto maior a barra, mais o preço acompanhou o sentimento das notícias com esse atraso.
        </div>
      </div>
    );
  }
  return null;
}

export default function CorrelationBarChart({ items = [], loading = false }) {
  if (loading) {
    return (
      <div className="h-48 w-full flex items-center justify-center bg-slate-50/50 rounded-lg">
        <div className="w-5 h-5 border-2 border-[#1a3c34] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Transform CorrelationItem list to grouped dataset by lag (t+0 to t+5)
  const lagMap = {};
  for (let i = 0; i <= 5; i++) {
    lagMap[i] = {
      lag: `t+${i}`,
      defasagem: i,
      interno: null,
      externo: null,
    };
  }

  if (items && items.length > 0) {
    items.forEach((item) => {
      const d = item.defasagem_dias;
      if (lagMap[d] !== undefined) {
        if (item.mercado === 'interno' || item.praca === 'parana') {
          lagMap[d].interno = item.pearson;
        } else if (item.mercado === 'externo' || item.praca === 'paranagua') {
          lagMap[d].externo = item.pearson;
        }
      }
    });
  }

  const chartData = Object.values(lagMap);

  return (
    <div className="w-full">
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis
              dataKey="lag"
              tickLine={false}
              axisLine={{ stroke: '#CBD5E1' }}
              tick={{ fill: '#64748B', fontSize: 11 }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#64748B', fontSize: 10 }}
              tickFormatter={(v) => Number(v).toFixed(2)}
              domain={[-0.05, 0.16]}
            />
            <ReferenceLine y={0} stroke="#94A3B8" strokeWidth={0.8} />
            <Tooltip content={<CustomTooltip />} />
            {/* Interno - Paraná */}
            <Bar
              dataKey="interno"
              name="Interno · Paraná"
              fill="#164e63"
              radius={[3, 3, 0, 0]}
              maxBarSize={22}
            />
            {/* Externo - Paranaguá */}
            <Bar
              dataKey="externo"
              name="Externo · Paranaguá"
              fill="#0284c7"
              radius={[3, 3, 0, 0]}
              maxBarSize={22}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Mockup styled legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-3 text-xs text-slate-600">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-[#164e63] inline-block" />
            <span className="font-medium text-slate-700">Interno · Paraná</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-[#0284c7] inline-block" />
            <span className="font-medium text-slate-700">Externo · Paranaguá</span>
          </div>
        </div>
        <span className="text-[11px] text-slate-400 font-medium">
          Eixo X: dias decorridos após a notícia
        </span>
      </div>
    </div>
  );
}
