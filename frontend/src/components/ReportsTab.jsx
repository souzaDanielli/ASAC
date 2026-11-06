import React, { useState, useEffect } from 'react';
import { Download, Sparkles, Printer, FileText, CheckCircle2, Building2, Anchor } from 'lucide-react';
import PriceSentimentChart from './Charts/PriceSentimentChart';
import CorrelationBarChart from './Charts/CorrelationBarChart';
import { fetchReport, fetchTimeseries, fetchCorrelation, fetchSummary } from '../api/client';

export default function ReportsTab() {
  const [report, setReport] = useState(null);
  const [timeseriesData, setTimeseriesData] = useState([]);
  const [correlationData, setCorrelationData] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [selectedPraca, setSelectedPraca] = useState('parana');
  const [loading, setLoading] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(false);

  const loadSummaryForPraca = async (praca) => {
    try {
      setLoadingSummary(true);
      const sumRes = await fetchSummary({ periodo: '2023-2026', praca });
      setSummaryData(sumRes);
    } catch (err) {
      console.error('Erro ao carregar resumo:', err);
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    Promise.all([
      fetchReport(),
      fetchTimeseries({ frequencia: 'semanal' }),
      fetchCorrelation(),
      fetchSummary({ periodo: '2023-2026', praca: 'parana' }),
    ])
      .then(([repRes, timeRes, corrRes, sumRes]) => {
        setReport(repRes);
        setTimeseriesData(timeRes || []);
        setCorrelationData(corrRes?.resultados || []);
        setSummaryData(sumRes);
      })
      .catch((err) => console.error('Erro ao montar relatório:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectPraca = (praca) => {
    setSelectedPraca(praca);
    loadSummaryForPraca(praca);
  };

  const handleExportPdf = () => {
    window.print();
  };

  const formattedDate = report?.gerado_em
    ? new Date(report.gerado_em).toLocaleDateString('pt-BR')
    : '28/10/2026';

  return (
    <div className="space-y-6 pb-16 print:p-0 print:space-y-4">
      {/* Header Row with Export PDF Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            {report?.titulo || 'Relatório consolidado de sentimento de notícias e preços CEPEA'}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Gerado em {formattedDate} · Notícias 2023–2026 · Preços 2020–2026
          </p>
        </div>

        <button
          onClick={handleExportPdf}
          className="print:hidden inline-flex items-center gap-2 bg-[#1a3c34] hover:bg-[#143029] text-white px-5 py-2 rounded-md text-xs font-semibold transition-colors card-shadow self-start sm:self-auto cursor-pointer"
        >
          <Download className="w-4 h-4" />
          Exportar PDF
        </button>
      </div>

      {/* Resumo Geral Executivo (Metodológico e Amostral) */}
      <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow space-y-2">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#1a3c34]" />
          <h2 className="text-sm font-bold text-slate-900">Resumo Executivo do Relatório</h2>
        </div>
        <p className="text-xs leading-relaxed text-slate-700 bg-slate-50/70 p-4 rounded-md border border-slate-100">
          {report?.resumo_geral ||
            'Relatório executivo integrando o acompanhamento temporal de notícias agrícolas da soja com os pregões de fechamento do indicador CEPEA/ESALQ. A estrutura investiga a concomitância estatística entre a polaridade líquida do sentimento textual e a dinâmica de preços, avaliando defasagens temporais sem pressuposição de causalidade determinística.'}
        </p>
      </div>

      {/* Série Temporal: Sentimento x Preço */}
      <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <h2 className="text-sm font-bold text-slate-900">
            Série temporal: sentimento x preço (média semanal)
          </h2>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-50 border border-amber-200 text-[11px] text-amber-900 font-medium">
            <span>📍 Praça no relatório: <strong>Média Ponderada (Paraná + Paranaguá)</strong></span>
          </div>
        </div>
        <div className="text-xs font-semibold text-slate-400 mb-1">R$</div>
        <PriceSentimentChart data={timeseriesData} loading={loading} />
      </div>

      {/* Side-by-Side: Correlação de Pearson & Resumo IA por Praça */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Correlação de Pearson */}
        <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between pb-2 border-b border-slate-100 gap-2">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Correlação de Pearson por defasagem
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Tempo de resposta dos preços após as notícias
                </p>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded shrink-0">
                Pico em t+2
              </span>
            </div>

            <div className="mt-3 bg-slate-50/80 p-2.5 rounded-md border border-slate-200/80 text-[11px] text-slate-600 leading-relaxed">
              <span><strong>Defasagem (t+0 a t+5):</strong> mede quantos dias de atraso o mercado leva para refletir o teor das notícias na cotação. O ponto de maior reação no Paraná ocorre em <strong>t+2 (2 dias úteis)</strong> com correlação de <strong>+0,1037</strong>.</span>
            </div>

            <div className="mt-4">
              <CorrelationBarChart items={correlationData} loading={loading} />
            </div>
          </div>
        </div>

        {/* Right: Resumo Analítico da IA (com seletor de praça) */}
        <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                Análise Econômica por IA
              </h3>

              {/* Seletor Paraná vs Paranaguá */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-md text-[11px]">
                <button
                  onClick={() => handleSelectPraca('parana')}
                  className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1 ${
                    selectedPraca === 'parana'
                      ? 'bg-white text-[#1a3c34] font-bold shadow-xs'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Building2 className="w-3 h-3" />
                  Paraná
                </button>
                <button
                  onClick={() => handleSelectPraca('paranagua')}
                  className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1 ${
                    selectedPraca === 'paranagua'
                      ? 'bg-white text-[#1a3c34] font-bold shadow-xs'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Anchor className="w-3 h-3" />
                  Paranaguá
                </button>
              </div>
            </div>

            <div className="mt-4 text-xs leading-relaxed text-slate-700 bg-slate-50/70 p-4 rounded-md border border-slate-100 min-h-[110px]">
              {loadingSummary ? (
                <div className="space-y-2 animate-pulse py-2">
                  <div className="h-3 bg-slate-200 rounded w-full" />
                  <div className="h-3 bg-slate-200 rounded w-5/6" />
                  <div className="h-3 bg-slate-200 rounded w-4/6" />
                </div>
              ) : summaryData?.texto ? (
                <p>{summaryData.texto}</p>
              ) : (
                <p className="text-slate-500 italic">
                  Análise econômica para {selectedPraca === 'parana' ? 'o Mercado Interno (Paraná)' : 'o Porto Exportador (Paranaguá)'}.
                </p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Fonte: {summaryData?.fonte || 'gerado'} · modelo {summaryData?.modelo_llm || 'gemini-2.0-flash'}</span>
            <span>Praça: {selectedPraca === 'parana' ? 'Paraná' : 'Paranaguá'}</span>
          </div>
        </div>
      </div>

      {/* Insights Principais */}
      <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow">
        <h2 className="text-sm font-bold text-slate-900 mb-3">Insights principais</h2>
        <ul className="space-y-2 text-xs text-slate-700">
          {report?.insights_principais?.length ? (
            report.insights_principais.map((insight, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-700 font-bold">•</span>
                <span>{insight}</span>
              </li>
            ))
          ) : (
            <>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700 font-bold">•</span>
                <span>6.320 notícias tratadas e associadas ao próximo pregão útil do CEPEA.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700 font-bold">•</span>
                <span>Preços cobrindo Paraná e Paranaguá.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700 font-bold">•</span>
                <span>As correlações temporais não pressupõem causalidade.</span>
              </li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}
