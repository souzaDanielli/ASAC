import React, { useState, useEffect } from 'react';
import { ExternalLink, X, Search, ChevronLeft, ChevronRight, FileText, RotateCcw, AlertCircle, RefreshCw } from 'lucide-react';
import { fetchNews } from '../api/client';

export default function NewsTab() {
  const [news, setNews] = useState([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(6320);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [mercado, setMercado] = useState('todos');
  const [sentimento, setSentimento] = useState('todos');
  const [origemRotulo, setOrigemRotulo] = useState('todas');
  const [dataInicio, setDataInicio] = useState('2023-01-02');
  const [dataFim, setDataFim] = useState('2026-09-03');

  // Selected news item for full reading modal
  const [selectedNews, setSelectedNews] = useState(null);

  const loadData = async (targetPage = 1, overrideFilters = null) => {
    try {
      setLoading(true);
      setError(null);

      const fMercado = overrideFilters ? overrideFilters.mercado : mercado;
      const fSentimento = overrideFilters ? overrideFilters.sentimento : sentimento;
      const fOrigem = overrideFilters ? overrideFilters.origemRotulo : origemRotulo;
      const fInicio = overrideFilters ? overrideFilters.dataInicio : dataInicio;
      const fFim = overrideFilters ? overrideFilters.dataFim : dataFim;

      const res = await fetchNews({
        page: targetPage,
        pageSize,
        mercado: fMercado,
        sentimento: fSentimento,
        origem_rotulo: fOrigem,
        data_inicio: fInicio,
        data_fim: fFim,
      });

      setNews(res.items || []);
      setTotalPages(res.total_pages || 1);
      setTotalItems(res.total || 0);
      setPage(res.page || 1);
    } catch (err) {
      console.error('Erro ao listar notícias:', err);
      setError('Houve uma lentidão ao consultar o banco. Clique em "Tentar novamente".');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(1);
  }, []);

  const handleFilter = (e) => {
    e.preventDefault();
    loadData(1);
  };

  const handleResetFilters = () => {
    const defaults = {
      mercado: 'todos',
      sentimento: 'todos',
      origemRotulo: 'todas',
      dataInicio: '2023-01-02',
      dataFim: '2026-09-03',
    };
    setMercado(defaults.mercado);
    setSentimento(defaults.sentimento);
    setOrigemRotulo(defaults.origemRotulo);
    setDataInicio(defaults.dataInicio);
    setDataFim(defaults.dataFim);
    loadData(1, defaults);
  };

  const formatDate = (isoOrStr) => {
    if (!isoOrStr) return '-';
    if (isoOrStr.includes('-')) {
      const parts = isoOrStr.split(' ')[0].split('-');
      if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
      }
    }
    return isoOrStr;
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Notícias classificadas
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          {totalItems.toLocaleString('pt-BR')} notícias · 611 rotuladas manualmente
        </p>
      </div>

      {/* Filter Bar Box */}
      <div className="bg-white p-5 rounded-lg border border-slate-200/90 card-shadow">
        <form onSubmit={handleFilter} className="flex flex-wrap items-end gap-3 text-xs">
          {/* Mercado */}
          <div className="flex flex-col gap-1 min-w-[110px]">
            <label className="text-slate-500 font-medium">Mercado</label>
            <select
              value={mercado}
              onChange={(e) => setMercado(e.target.value)}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none"
            >
              <option value="todos">Todos</option>
              <option value="interno">Interno</option>
              <option value="externo">Externo</option>
            </select>
          </div>

          {/* Sentimento */}
          <div className="flex flex-col gap-1 min-w-[110px]">
            <label className="text-slate-500 font-medium">Sentimento</label>
            <select
              value={sentimento}
              onChange={(e) => setSentimento(e.target.value)}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none"
            >
              <option value="todos">Todos</option>
              <option value="positivo">Positivo</option>
              <option value="negativo">Negativo</option>
              <option value="neutro">Neutro</option>
            </select>
          </div>

          {/* Origem do rótulo */}
          <div className="flex flex-col gap-1 min-w-[120px]">
            <label className="text-slate-500 font-medium">Origem do rótulo</label>
            <select
              value={origemRotulo}
              onChange={(e) => setOrigemRotulo(e.target.value)}
              className="bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-700 text-xs focus:ring-1 focus:ring-[#1a3c34] focus:border-[#1a3c34] outline-none"
            >
              <option value="todas">Todas</option>
              <option value="manual">Manual</option>
              <option value="modelo">Modelo</option>
            </select>
          </div>

          {/* Data início */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Data início</label>
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

          {/* Data fim */}
          <div className="flex flex-col gap-1">
            <label className="text-slate-500 font-medium">Data fim</label>
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

          {/* Botões */}
          <div className="flex items-center gap-2">
            <button
              type="submit"
              className="bg-[#1a3c34] hover:bg-[#143029] text-white px-5 py-1.5 rounded-md text-xs font-semibold transition-colors card-shadow cursor-pointer flex items-center gap-1.5"
            >
              {loading && <RefreshCw className="w-3 h-3 animate-spin" />}
              Filtrar
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              title="Restaurar datas e filtros padrão"
              className="border border-slate-300 hover:bg-slate-100 text-slate-600 px-3 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              Limpar
            </button>
          </div>
        </form>
      </div>

      {/* Table Container */}
      <div className="bg-white rounded-lg border border-slate-200/90 card-shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-slate-500 font-semibold">
                <th className="py-3 px-4 w-28">Data</th>
                <th className="py-3 px-4">Título</th>
                <th className="py-3 px-4 w-28">Mercado</th>
                <th className="py-3 px-4 w-28">Sentimento</th>
                <th className="py-3 px-4 w-24">Rótulo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-5 h-5 border-2 border-[#1a3c34] border-t-transparent rounded-full animate-spin" />
                      <span>Carregando notícias...</span>
                    </div>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-rose-600">
                    <div className="flex flex-col items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      <span>{error}</span>
                      <button
                        onClick={() => loadData(page)}
                        className="mt-1 px-3 py-1 bg-[#1a3c34] text-white rounded text-xs cursor-pointer"
                      >
                        Tentar novamente
                      </button>
                    </div>
                  </td>
                </tr>
              ) : news.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500 space-y-2">
                    <p>Nenhuma notícia encontrada para a combinação de filtros selecionada.</p>
                    <button
                      onClick={handleResetFilters}
                      className="px-3 py-1 text-xs text-[#1a3c34] font-semibold underline cursor-pointer"
                    >
                      Restaurar filtros padrão
                    </button>
                  </td>
                </tr>
              ) : (
                news.map((item) => {
                  const sent = item.sentimento?.toLowerCase();
                  let badgeClass = 'bg-slate-100 text-slate-600 border-slate-200';
                  if (sent === 'positivo') {
                    badgeClass = 'bg-[#ECFDF5] text-[#059669] border-[#A7F3D0]';
                  } else if (sent === 'negativo') {
                    badgeClass = 'bg-[#FEF2F2] text-[#DC2626] border-[#FECACA]';
                  }

                  return (
                    <tr
                      key={item.id}
                      className="hover:bg-slate-50/80 transition-colors group cursor-pointer"
                      onClick={() => setSelectedNews(item)}
                    >
                      {/* Data */}
                      <td className="py-3 px-4 font-mono text-slate-600 whitespace-nowrap">
                        {formatDate(item.data_dia || item.data)}
                      </td>

                      {/* Título */}
                      <td className="py-3 px-4 font-medium text-slate-800">
                        <span className="group-hover:text-[#1a3c34] group-hover:underline transition-colors line-clamp-1">
                          {item.titulo}
                        </span>
                      </td>

                      {/* Mercado */}
                      <td className="py-3 px-4 text-slate-600 capitalize">
                        {item.mercado || '-'}
                      </td>

                      {/* Sentimento */}
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2.5 py-0.5 text-[11px] font-medium rounded-full border ${badgeClass} capitalize`}
                        >
                          {item.sentimento || '-'}
                        </span>
                      </td>

                      {/* Rótulo */}
                      <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                        {item.origem_rotulo || 'modelo'}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination matching mockup */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
          <div>
            Página <span className="font-semibold text-slate-800">{page}</span> de{' '}
            <span className="font-semibold text-slate-800">{totalPages}</span>
            <span className="text-slate-400 ml-2">({totalItems} registros)</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => loadData(page - 1)}
              disabled={page <= 1 || loading}
              className="px-4 py-1.5 border border-slate-300 rounded-md font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
            >
              Anterior
            </button>
            <button
              onClick={() => loadData(page + 1)}
              disabled={page >= totalPages || loading}
              className="px-4 py-1.5 bg-[#1a3c34] hover:bg-[#143029] text-white rounded-md font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors card-shadow cursor-pointer"
            >
              Próxima
            </button>
          </div>
        </div>
      </div>

      {/* News Details Modal */}
      {selectedNews && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-100 flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-1.5">
                  <span className="font-mono">{formatDate(selectedNews.data_dia || selectedNews.data)}</span>
                  <span>•</span>
                  <span className="capitalize font-medium text-slate-700">Mercado {selectedNews.mercado}</span>
                  <span>•</span>
                  <span className="uppercase text-[10px] font-bold text-slate-400">Rótulo: {selectedNews.origem_rotulo}</span>
                </div>
                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {selectedNews.titulo}
                </h3>
              </div>
              <button
                onClick={() => setSelectedNews(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-100 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-5 overflow-y-auto space-y-4 text-xs leading-relaxed text-slate-600">
              {selectedNews.subtitulo && (
                <p className="font-medium text-slate-800 italic bg-slate-50 p-3 rounded border border-slate-100">
                  {selectedNews.subtitulo}
                </p>
              )}

              <div className="whitespace-pre-line text-slate-700">
                {selectedNews.texto || 'Conteúdo integral não disponível no resumo do banco.'}
              </div>

              {selectedNews.data_pregao && (
                <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                  Associado ao pregão CEPEA de:{' '}
                  <span className="font-semibold text-slate-600 font-mono">
                    {formatDate(selectedNews.data_pregao)}
                  </span>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50/60 flex items-center justify-between">
              {selectedNews.link ? (
                <a
                  href={selectedNews.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1a3c34] hover:underline"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Ver notícia original no Canal Rural
                </a>
              ) : (
                <span className="text-[11px] text-slate-400 italic">Link externo indisponível</span>
              )}
              <button
                onClick={() => setSelectedNews(null)}
                className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-medium rounded-md transition-colors cursor-pointer"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
