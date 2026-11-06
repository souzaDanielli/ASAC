import React, { useState, useEffect } from 'react';
import { Sparkles, Calendar, TrendingUp, Layers, HelpCircle, ArrowUpRight, Info, ChevronDown, ChevronUp, RefreshCw, AlertCircle } from 'lucide-react';
import PriceSentimentChart from './Charts/PriceSentimentChart';
import CorrelationBarChart from './Charts/CorrelationBarChart';
import { fetchTimeseries, fetchCorrelation, fetchSummary, fetchModelMetrics } from '../api/client';

export default function OverviewTab({ healthData }) {
  // Chart filter states
  const [frequencia, setFrequencia] = useState('semanal');
  const [mercado, setMercado] = useState('todos');
  const [dataInicio, setDataInicio] = useState('2023-01-02');
  const [dataFim, setDataFim] = useState('2026-09-03');

  // Educational toggle
  const [showExplanation, setShowExplanation] = useState(true);

  // AI Summary Market selector
  const [resumoPraca, setResumoPraca] = useState('parana');

  // Data states
  const [timeseriesData, setTimeseriesData] = useState([]);
  const [correlationData, setCorrelationData] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [modelAccuracy, setModelAccuracy] = useState('43.86%');

  // Loading states
  const [loadingChart, setLoadingChart] = useState(true);
  const [loadingCorr, setLoadingCorr] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [chartError, setChartError] = useState(null);

  // Load timeseries on filter apply
  const loadTimeseries = async (customFreq, customMercado) => {
    try {
      setLoadingChart(true);
      setChartError(null);
      const freq = typeof customFreq === 'string' ? customFreq : frequencia;
      const merc = typeof customMercado === 'string' ? customMercado : mercado;

      const data = await fetchTimeseries({
        frequencia: freq,
        mercado: merc === 'todos' ? undefined : merc,
        data_inicio: dataInicio,
        data_fim: dataFim,
      });
      setTimeseriesData(data || []);
    } catch (err) {
      console.error('Erro ao buscar timeseries:', err);
      setChartError('Não foi possível carregar os dados temporais no momento.');
    } finally {
      setLoadingChart(false);
    }
  };

  const loadSummary = async (praca) => {
    try {
      setLoadingSummary(true);
      const res = await fetchSummary({ periodo: '2023-2026', praca });
      setSummaryData(res);
    } catch (err) {
      console.error('Erro ao buscar resumo IA:', err);
    } finally {
      setLoadingSummary(false);
    }
  };

  // Load correlation and summary on mount
  useEffect(() => {
    loadTimeseries();

    // Fetch correlation
    fetchCorrelation()
      .then((res) => setCorrelationData(res.resultados || []))
      .catch((err) => console.error('Erro ao buscar correlacao:', err))
      .finally(() => setLoadingCorr(false));

    // Fetch AI Summary
    loadSummary(resumoPraca);

    // Fetch Model Accuracy
    fetchModelMetrics()
      .then((res) => {
        if (res.metricas_gerais && res.metricas_gerais.length > 0) {
          const acc = res.metricas_gerais[0].acuracia;
          if (acc != null) {
            setModelAccuracy(`${(acc * 100).toFixed(2)}%`);
          }
        }
      })
      .catch((err) => console.error('Erro ao buscar acuracia:', err));
  }, []);

  const totalNoticias = healthData?.total_noticias?.toLocaleString('pt-BR') || '6.320';
  const totalPregoes = healthData?.total_precos ? Math.floor(healthData.total_precos / 2).toLocaleString('pt-BR') : '1.417';

  return (
    <div className="space-y-6 pb-12">
      {/* Title & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Visão geral
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Sentimento das notícias x preço da soja (CEPEA)
          </p>
        </div>

        {/* Botão de ajuda / explicação do índice */}
        <button
          onClick={() => setShowExplanation(!showExplanation)}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[#1a3c34] bg-emerald-50 hover:bg-emerald-100 border border-emerald-200/80 px-3 py-1.5 rounded-md transition-colors self-start sm:self-auto"
        >
          <Info className="w-4 h-4 text-emerald-700" />
          <span>{showExplanation ? 'Ocultar explicação do índice' : 'Entenda o índice de sentimento'}</span>
          {showExplanation ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Card Explicativo: O que é o Índice de Sentimento */}
      {showExplanation && (
        <div className="bg-gradient-to-r from-emerald-50/70 via-slate-50 to-amber-50/50 p-5 rounded-lg border border-emerald-200/80 card-shadow text-xs space-y-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800 text-sm flex items-center gap-1.5">
              💡 Por que o sentimento aparece como número no gráfico?
            </span>
          </div>

          <p className="text-slate-600 leading-relaxed">
            Cada notícia individual recebe um rótulo qualitativo (<span className="text-emerald-700 font-semibold">positivo</span>, <span className="text-slate-600 font-semibold">neutro</span> ou <span className="text-rose-700 font-semibold">negativo</span>). Porém, para comparar matematicamente com a cotação da saca de soja em reais (<span className="text-amber-800 font-semibold">R$/saca</span>) e medir a correlação estatística, todas as notícias de cada período são consolidadas em um <strong>Índice de Polaridade Líquida</strong>:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
            {/* Fórmula */}
            <div className="bg-white/80 p-3 rounded border border-slate-200/80 space-y-1">
              <span className="font-semibold text-slate-700 block">Fórmula de Cálculo:</span>
              <div className="font-mono text-center text-slate-800 font-bold bg-slate-100 py-1.5 px-2 rounded">
                (Positivas - Negativas) ÷ Total
              </div>
              <span className="text-[11px] text-slate-400 block text-center">As neutras amortecem a escala</span>
            </div>

            {/* Escala Visual */}
            <div className="bg-white/80 p-3 rounded border border-slate-200/80 md:col-span-2 space-y-1.5">
              <span className="font-semibold text-slate-700 block">Como ler os valores no eixo direito (-1.0 a +1.0):</span>
              <div className="relative pt-1">
                <div className="h-2.5 rounded-full bg-gradient-to-r from-rose-500 via-slate-300 to-emerald-500 w-full" />
                <div className="flex justify-between text-[11px] font-mono font-medium pt-1">
                  <span className="text-rose-700">-1.0 (100% Baixa)</span>
                  <span className="text-slate-500">0.0 (Neutro / Equilíbrio)</span>
                  <span className="text-emerald-700">+1.0 (100% Alta)</span>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 pt-0.5">
                Exemplo: Um índice de <strong className="font-mono text-emerald-700">+0.25</strong> indica que notícias de alta superaram as de queda por ampla margem naquela semana.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Notícias */}
        <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
          <p className="text-xs font-medium text-slate-500">Notícias</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalNoticias}</p>
        </div>

        {/* Pregões */}
        <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
          <p className="text-xs font-medium text-slate-500">Pregões</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{totalPregoes}</p>
        </div>

        {/* Notícias - período */}
        <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
          <p className="text-xs font-medium text-slate-500">Notícias · período</p>
          <p className="text-lg font-bold text-slate-900 mt-2">
            02/01/2023 a 03/09/2026
          </p>
        </div>

        {/* Acurácia do modelo */}
        <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
          <p className="text-xs font-medium text-slate-500">Acurácia do modelo</p>
          <p className="text-2xl font-bold text-slate-900 mt-1 font-mono">
            [{modelAccuracy}]
          </p>
        </div>
      </div>

      {/* Main Chart Card: Sentimento x Preço */}
      <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Sentimento x preço da soja
            </h2>
            <p className="text-xs text-slate-500">
              Sobreposição temporal entre a polaridade das notícias e cotações CEPEA/ESALQ
            </p>
          </div>

          {/* Aviso dinâmico de Praça de Referência */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs border bg-amber-50/80 border-amber-200/90 text-amber-900 shadow-xs self-start sm:self-auto">
            <span className="font-semibold text-amber-950">📍 Cotação da saca:</span>
            {mercado === 'interno' && (
              <span><strong>Paraná</strong> (Mercado Físico Disponível)</span>
            )}
            {mercado === 'externo' && (
              <span><strong>Paranaguá</strong> (Porto Exportador FOB)</span>
            )}
            {mercado === 'todos' && (
              <span><strong>Média das Praças</strong> (Paraná + Paranaguá)</span>
            )}
          </div>
        </div>

        {/* Filter Controls Row */}
        <div className="mt-4 flex flex-wrap items-end gap-3 text-xs">
          {/* Frequência */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Frequência</label>
            <select
              value={frequencia}
              onChange={(e) => {
                const val = e.target.value;
                setFrequencia(val);
                loadTimeseries(val, mercado);
              }}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none cursor-pointer"
            >
              <option value="semanal">Semanal (Média da Semana)</option>
              <option value="diario">Diário (Fechamento do Dia)</option>
            </select>
          </div>

          {/* Mercado */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Mercado</label>
            <select
              value={mercado}
              onChange={(e) => {
                const val = e.target.value;
                setMercado(val);
                loadTimeseries(frequencia, val);
              }}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none cursor-pointer"
            >
              <option value="todos">Todos (Média PR + PG)</option>
              <option value="interno">Interno (Paraná)</option>
              <option value="externo">Externo (Paranaguá)</option>
            </select>
          </div>

          {/* Início */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Início</label>
            <input
              type="date"
              value={dataInicio}
              max={dataFim || undefined}
              onChange={(e) => {
                const val = e.target.value;
                setDataInicio(val);
                if (dataFim && val > dataFim) setDataFim(val);
              }}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none font-mono"
            />
          </div>

          {/* Fim */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Fim</label>
            <input
              type="date"
              value={dataFim}
              min={dataInicio || undefined}
              onChange={(e) => {
                const val = e.target.value;
                setDataFim(val);
                if (dataInicio && val < dataInicio) setDataInicio(val);
              }}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none font-mono"
            />
          </div>

          {/* Aplicar Button */}
          <button
            onClick={() => loadTimeseries()}
            className="bg-[#1a3c34] hover:bg-[#143029] text-white px-5 py-1.5 rounded-md text-xs font-semibold transition-colors card-shadow flex items-center gap-1.5 cursor-pointer"
          >
            {loadingChart && <RefreshCw className="w-3 h-3 animate-spin" />}
            Aplicar
          </button>
        </div>

        {/* Dual-axis Chart Container */}
        <div className="mt-6">
          <div className="flex justify-between items-center text-xs font-semibold text-slate-400 mb-1">
            <span>R$ (Preço da Saca)</span>
            <span>Índice de Polaridade (-1 a +1)</span>
          </div>

          {chartError ? (
            <div className="h-72 w-full flex flex-col items-center justify-center bg-slate-50/50 rounded-lg text-xs text-rose-600 gap-2">
              <AlertCircle className="w-5 h-5" />
              <span>{chartError}</span>
              <button
                onClick={() => loadTimeseries()}
                className="mt-1 px-3 py-1 bg-[#1a3c34] text-white rounded text-xs cursor-pointer"
              >
                Tentar novamente
              </button>
            </div>
          ) : (
            <PriceSentimentChart data={timeseriesData} loading={loadingChart} />
          )}
        </div>
      </div>

      {/* Two Column Section at Bottom */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Card: Correlação sentimento x preço */}
        <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between pb-2 border-b border-slate-100 gap-2">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Correlação sentimento x preço
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Tempo de reação: mede quantos dias o preço leva para absorver o tom das notícias
                </p>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded shrink-0">
                Pico em t+2 (2 dias)
              </span>
            </div>

            {/* Caixa Didática Explicativa Permanente */}
            <div className="mt-3 bg-slate-50/80 p-3 rounded-md border border-slate-200/80 text-[11px] text-slate-600 space-y-1.5 leading-relaxed">
              <div className="flex items-center gap-1.5 font-bold text-slate-800">
                <Info className="w-3.5 h-3.5 text-[#1a3c34]" />
                <span>O que significa a defasagem (t+0 a t+5)?</span>
              </div>
              <ul className="space-y-0.5 pl-1 text-slate-600">
                <li>• <strong>t+0 (mesmo dia):</strong> sintonia do preço no próprio dia em que a notícia foi publicada.</li>
                <li>• <strong>t+1 a t+5 (dias seguintes):</strong> sintonia do preço de 1 a 5 dias após a publicação.</li>
                <li>• <strong>Altura da barra:</strong> quanto mais alta, maior a tendência de alta de preços após notícias positivas. No Paraná, a barra é máxima em <strong>t+2 (+0,1037)</strong>, mostrando que o mercado físico leva cerca de <strong>2 dias</strong> para digerir as notícias.</li>
              </ul>
            </div>

            <div className="mt-4">
              <CorrelationBarChart items={correlationData} loading={loadingCorr} />
            </div>
          </div>
        </div>

        {/* Right Card: Resumo gerado por IA */}
        <div className="bg-white p-6 rounded-lg border border-slate-200/90 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                Resumo gerado por IA
              </h3>

              {/* Seletor de praça para o resumo */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-md text-[11px]">
                <button
                  onClick={() => {
                    setResumoPraca('parana');
                    loadSummary('parana');
                  }}
                  className={`px-2.5 py-1 rounded transition-colors ${
                    resumoPraca === 'parana'
                      ? 'bg-white text-[#1a3c34] font-bold shadow-xs'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Paraná
                </button>
                <button
                  onClick={() => {
                    setResumoPraca('paranagua');
                    loadSummary('paranagua');
                  }}
                  className={`px-2.5 py-1 rounded transition-colors ${
                    resumoPraca === 'paranagua'
                      ? 'bg-white text-[#1a3c34] font-bold shadow-xs'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Paranaguá
                </button>
              </div>
            </div>

            <div className="mt-4 text-xs leading-relaxed text-slate-600 space-y-2">
              {loadingSummary ? (
                <div className="space-y-2 animate-pulse">
                  <div className="h-3 bg-slate-200 rounded w-full" />
                  <div className="h-3 bg-slate-200 rounded w-5/6" />
                  <div className="h-3 bg-slate-200 rounded w-4/6" />
                </div>
              ) : summaryData?.texto ? (
                <p className="text-slate-700 bg-slate-50/70 p-3.5 rounded-md border border-slate-100">
                  {summaryData.texto}
                </p>
              ) : (
                <p className="text-slate-500 italic">
                  Com base na análise das notícias para a praça selecionada, foram avaliadas as tendências temporais e associações estatísticas sem pressuposição de causalidade direta.
                </p>
              )}
            </div>
          </div>

          <div className="mt-6 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Fonte: {summaryData?.fonte || 'gerado'} · modelo {summaryData?.modelo_llm || 'gemini-2.0-flash'} · gerado em {summaryData?.gerado_em ? new Date(summaryData.gerado_em).toLocaleDateString('pt-BR') : '28/10/2026'}
          </div>
        </div>
      </div>
    </div>
  );
}
