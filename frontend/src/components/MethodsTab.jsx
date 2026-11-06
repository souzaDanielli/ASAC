import React, { useState, useEffect } from 'react';
import { fetchMethods, fetchModelMetrics } from '../api/client';
import { CheckCircle2, Award, Cpu, BookOpen, Layers } from 'lucide-react';

export default function MethodsTab() {
  const [methodsData, setMethodsData] = useState(null);
  const [metricsData, setMetricsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchMethods(), fetchModelMetrics()])
      .then(([methodsRes, metricsRes]) => {
        setMethodsData(methodsRes);
        setMetricsData(metricsRes);
      })
      .catch((err) => console.error('Erro ao carregar dados de metodologia:', err))
      .finally(() => setLoading(false));
  }, []);

  // Primary model metrics
  const primaryMetric = metricsData?.metricas_gerais?.[0] || {};
  const acuracia = primaryMetric.acuracia != null ? (primaryMetric.acuracia * 100).toFixed(2).replace('.', ',') + '%' : '[0,00]';
  const precisao = primaryMetric.precisao != null ? (primaryMetric.precisao * 100).toFixed(2).replace('.', ',') + '%' : '[0,00]';
  const recall = primaryMetric.recall != null ? (primaryMetric.recall * 100).toFixed(2).replace('.', ',') + '%' : '[0,00]';
  const f1 = primaryMetric.f1 != null ? (primaryMetric.f1 * 100).toFixed(2).replace('.', ',') + '%' : '[0,00]';

  // 4 steps of methodology matching mockup
  const methodSteps = [
    {
      num: 1,
      title: 'Coleta das notícias',
      desc: 'Raspagem de 6.320 notícias agrícolas focadas na cultura da soja no portal Canal Rural, entre janeiro de 2023 e setembro de 2026.',
    },
    {
      num: 2,
      title: 'Pré-processamento',
      desc: methodsData?.preprocessamento?.regras?.[0] || 'Remoção de duplicatas, normalização ortográfica, tratamento de pontuação e separação estrutural de título, corpo e subtítulo.',
    },
    {
      num: 3,
      title: 'Classificação de sentimento',
      desc: 'Classificação em 6 classes combinadas (mercado interno/externo x positivo/neutro/negativo) com 611 amostras manuais e validação cruzada 5-fold.',
    },
    {
      num: 4,
      title: 'Associação ao pregão CEPEA',
      desc: 'Alinhamento temporal conectando notícias publicadas à noite, fins de semana ou feriados ao pregão útil subsequente da saca de soja.',
    },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Metodologia e métricas
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Como os dados foram tratados e o quão assertivo é o classificador
        </p>
      </div>

      {/* 1. Métodos Utilizados */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-slate-900">Métodos utilizados</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {methodSteps.map((step) => (
            <div
              key={step.num}
              className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow flex flex-col justify-start"
            >
              <span className="text-2xl font-black text-amber-600/90 font-mono mb-2">
                {step.num}
              </span>
              <h3 className="text-sm font-bold text-slate-900 mb-1.5">
                {step.title}
              </h3>
              <p className="text-xs leading-relaxed text-slate-500">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Métricas de Assertividade */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-slate-900">Métricas de assertividade</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Acurácia */}
          <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
            <p className="text-xs font-medium text-slate-500">Acurácia</p>
            <p className="text-2xl font-bold text-slate-900 mt-2 font-mono">
              [{acuracia}]
            </p>
          </div>

          {/* Precisão */}
          <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
            <p className="text-xs font-medium text-slate-500">Precisão</p>
            <p className="text-2xl font-bold text-slate-900 mt-2 font-mono">
              [{precisao}]
            </p>
          </div>

          {/* Recall */}
          <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
            <p className="text-xs font-medium text-slate-500">Recall</p>
            <p className="text-2xl font-bold text-slate-900 mt-2 font-mono">
              [{recall}]
            </p>
          </div>

          {/* F1-score */}
          <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
            <p className="text-xs font-medium text-slate-500">F1-score</p>
            <p className="text-2xl font-bold text-slate-900 mt-2 font-mono">
              [{f1}]
            </p>
          </div>
        </div>
      </div>

      {/* 3. Estratégias Testadas */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-slate-900">Estratégias testadas</h2>

        <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {methodsData?.estrategias_testadas?.map((est, idx) => (
              <div
                key={est.id || idx}
                className="p-4 rounded-lg border border-slate-100 bg-slate-50/60 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-[#1a3c34] uppercase tracking-wider">
                    {est.nome}
                  </h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                    {est.id}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {est.descricao}
                </p>
                <div className="text-[11px] text-slate-400 pt-1 font-mono">
                  Modelo: <span className="text-slate-600 font-sans">{est.modelo}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Tabela de métricas comparativas no banco */}
          {metricsData?.metricas_gerais && metricsData.metricas_gerais.length > 0 && (
            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                Resultados Comparativos Gravados
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                      <th className="py-2.5 px-3">Estratégia</th>
                      <th className="py-2.5 px-3">Método Avaliação</th>
                      <th className="py-2.5 px-3 text-right">Acurácia</th>
                      <th className="py-2.5 px-3 text-right">Precisão</th>
                      <th className="py-2.5 px-3 text-right">Recall</th>
                      <th className="py-2.5 px-3 text-right">F1-Score</th>
                      <th className="py-2.5 px-3 text-right">Amostras</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {metricsData.metricas_gerais.map((m, i) => (
                      <tr key={i} className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-3 font-medium text-slate-800">{m.estrategia}</td>
                        <td className="py-2.5 px-3 text-slate-500">{m.metodo_avaliacao}</td>
                        <td className="py-2.5 px-3 text-right font-mono font-bold text-[#1a3c34]">
                          {(m.acuracia * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-right font-mono">
                          {(m.precisao * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-right font-mono">
                          {(m.recall * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-right font-mono">
                          {(m.f1 * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 text-right font-mono text-slate-500">
                          {m.amostras}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Métricas por Classe */}
          {metricsData?.metricas_por_classe && metricsData.metricas_por_classe.length > 0 && (
            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                Desempenho Detalhado por Classe (Validação Cruzada)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                      <th className="py-2 px-3">Classe</th>
                      <th className="py-2 px-3 text-right">Precisão</th>
                      <th className="py-2 px-3 text-right">Recall</th>
                      <th className="py-2 px-3 text-right">F1-Score</th>
                      <th className="py-2 px-3 text-right">Suporte (amostras)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {metricsData.metricas_por_classe
                      .filter((c) => c.estrategia.includes('validacao cruzada'))
                      .map((c, i) => (
                        <tr key={i} className="hover:bg-slate-50/50">
                          <td className="py-2 px-3 font-medium text-slate-700 capitalize">{c.classe}</td>
                          <td className="py-2 px-3 text-right font-mono">{(c.precisao * 100).toFixed(1)}%</td>
                          <td className="py-2 px-3 text-right font-mono">{(c.recall * 100).toFixed(1)}%</td>
                          <td className="py-2 px-3 text-right font-mono font-semibold text-slate-800">
                            {(c.f1 * 100).toFixed(1)}%
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-slate-500">{c.suporte}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

