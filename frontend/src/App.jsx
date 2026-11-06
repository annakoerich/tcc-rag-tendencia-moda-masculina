import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Brain,
  Package,
  AlertTriangle,
  ShoppingBag,
  Sparkles,
  Layers,
  PlusCircle,
  BarChart3,
  CheckCircle2,
  RefreshCw,
  HelpCircle,
  ArrowRight,
  Bot,
  Zap
} from 'lucide-react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiOnline, setApiOnline] = useState(false);

  const [kpis, setKpis] = useState(null);
  const [produtos, setProdutos] = useState([]);
  const [tendencias, setTendencias] = useState([]);
  const [recomendacoes, setRecomendacoes] = useState([]);

  const [briefing, setBriefing] = useState(null);
  const [loadingBriefing, setLoadingBriefing] = useState(false);

  const [ragPergunta, setRagPergunta] = useState('');
  const [ragCategoria, setRagCategoria] = useState('');
  const [ragProdutoId, setRagProdutoId] = useState('');
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResultado, setRagResultado] = useState(null);

  const [modalGerarTendencia, setModalGerarTendencia] = useState(false);
  const [temaIA, setTemaIA] = useState('Tendências Emergentes de Moda Masculina 2026');
  const [gerandoTendenciasIA, setGerandoTendenciasIA] = useState(false);

  const [avaliandoProdutoId, setAvaliandoProdutoId] = useState(null);
  const [resultadoAvaliacaoIA, setResultadoAvaliacaoIA] = useState(null);

  const [modalProduto, setModalProduto] = useState(false);
  const [novoProd, setNovoProd] = useState({
    nome: '',
    categoria: 'Camisas',
    preco_medio: '',
    custo_aquisicao: '',
    quantidade_estoque: '',
    estoque_minimo: 5,
    tendencia_score: 50
  });

  const perguntasExemplo = [
    { texto: 'Devo comprar mais calças jeans skinny para esta coleção?', cat: 'Calças' },
    { texto: 'Vale a pena investir em camisas de linho para o verão?', cat: 'Camisas' },
    { texto: 'O tênis de couro branco minimalista ainda tem giro seguro?', cat: 'Calçados' },
    { texto: 'Qual o risco de colocar bermudas de alfaiataria na vitrine?', cat: 'Bermudas' }
  ];

  const carregarDados = async () => {
    try {
      const statusRes = await fetch(`${API_BASE}/`);
      if (statusRes.ok) setApiOnline(true);

      const kpisRes = await fetch(`${API_BASE}/dashboard/kpis`);
      if (kpisRes.ok) {
        const kpiData = await kpisRes.json();
        setKpis(kpiData);
      }

      const prodRes = await fetch(`${API_BASE}/produtos/`);
      if (prodRes.ok) {
        const prodData = await prodRes.json();
        setProdutos(prodData);
      }

      const tendRes = await fetch(`${API_BASE}/tendencias/`);
      if (tendRes.ok) {
        const tendData = await tendRes.json();
        setTendencias(tendData);
      }

      const recRes = await fetch(`${API_BASE}/recomendacoes/`);
      if (recRes.ok) {
        const recData = await recRes.json();
        setRecomendacoes(recData);
      }
    } catch (err) {
      console.warn('API offline ou erro:', err);
      setApiOnline(false);
    }
  };

  const carregarBriefingIA = async () => {
    setLoadingBriefing(true);
    try {
      const res = await fetch(`${API_BASE}/ia/briefing-executivo`);
      if (res.ok) {
        const data = await res.json();
        setBriefing(data);
      }
    } catch (e) {
      console.warn('Erro ao obter briefing:', e);
    } finally {
      setLoadingBriefing(false);
    }
  };

  useEffect(() => {
    carregarDados();
    carregarBriefingIA();
  }, []);

  const executarConsultaRAG = async (perguntaTexto, catFiltro, prodId) => {
    const p = perguntaTexto || ragPergunta;
    if (!p.trim()) return;

    setRagLoading(true);
    try {
      const payload = {
        pergunta: p,
        categoria: catFiltro !== undefined ? catFiltro : (ragCategoria || null),
        produto_id: prodId !== undefined ? (prodId ? parseInt(prodId) : null) : (ragProdutoId ? parseInt(ragProdutoId) : null)
      };

      const res = await fetch(`${API_BASE}/rag/consultar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setRagResultado(data);
        carregarDados();
      }
    } catch (err) {
      alert('Erro ao consultar motor RAG: ' + err.message);
    } finally {
      setRagLoading(false);
    }
  };

  const gerarTendenciasComIA = async () => {
    setGerandoTendenciasIA(true);
    try {
      const res = await fetch(`${API_BASE}/ia/gerar-tendencias`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tema: temaIA })
      });
      if (res.ok) {
        const data = await res.json();
        alert(data.mensagem || 'Novas tendências geradas com sucesso!');
        setModalGerarTendencia(false);
        carregarDados();
      }
    } catch (err) {
      alert('Erro ao gerar tendências com IA: ' + err.message);
    } finally {
      setGerandoTendenciasIA(false);
    }
  };

  const avaliarProdutoComIA = async (prodId) => {
    setAvaliandoProdutoId(prodId);
    try {
      const res = await fetch(`${API_BASE}/ia/analisar-produto/${prodId}`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        setResultadoAvaliacaoIA(data);
        carregarDados();
      }
    } catch (err) {
      alert('Erro ao analisar produto com IA: ' + err.message);
    } finally {
      setAvaliandoProdutoId(null);
    }
  };

  const salvarNovoProduto = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        nome: novoProd.nome,
        categoria: novoProd.categoria,
        preco_medio: parseFloat(novoProd.preco_medio) || 0,
        custo_aquisicao: parseFloat(novoProd.custo_aquisicao) || 0,
        quantidade_estoque: parseInt(novoProd.quantidade_estoque) || 0,
        estoque_minimo: parseInt(novoProd.estoque_minimo) || 5,
        tendencia_score: parseFloat(novoProd.tendencia_score) || 50
      };

      const res = await fetch(`${API_BASE}/produtos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setModalProduto(false);
        setNovoProd({
          nome: '',
          categoria: 'Camisas',
          preco_medio: '',
          custo_aquisicao: '',
          quantidade_estoque: '',
          estoque_minimo: 5,
          tendencia_score: 50
        });
        carregarDados();
      }
    } catch (err) {
      alert('Erro ao cadastrar produto: ' + err.message);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-icon">
            <ShoppingBag size={24} />
          </div>
          <div>
            <h1 className="brand-title">Moda Inteligente</h1>
            <p className="brand-subtitle">Decisões Estratégicas e Inteligência de Mercado para o Varejo Masculino</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="api-status" style={{ backgroundColor: apiOnline ? '#ecfdf5' : '#fef2f2', color: apiOnline ? '#059669' : '#dc2626' }}>
            <div className="status-dot" style={{ backgroundColor: apiOnline ? '#10b981' : '#ef4444' }} />
            {apiOnline ? 'Serviço Operacional' : 'Aguardando API'}
          </div>
          <button onClick={carregarDados} className="badge" style={{ background: '#f1f5f9', color: '#475569', cursor: 'pointer', padding: '0.4rem 0.6rem' }}>
            <RefreshCw size={14} /> Atualizar
          </button>
        </div>
      </header>

      <nav className="tabs-bar">
        <button
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <BarChart3 size={18} /> Visão Geral & Briefing IA
        </button>
        <button
          className={`tab-btn ${activeTab === 'rag' ? 'active' : ''}`}
          onClick={() => setActiveTab('rag')}
        >
          <Brain size={18} /> Consultor RAG com IA
        </button>
        <button
          className={`tab-btn ${activeTab === 'tendencias' ? 'active' : ''}`}
          onClick={() => setActiveTab('tendencias')}
        >
          <TrendingUp size={18} /> Tendências & Descoberta IA
        </button>
        <button
          className={`tab-btn ${activeTab === 'produtos' ? 'active' : ''}`}
          onClick={() => setActiveTab('produtos')}
        >
          <Package size={18} /> Estoque & Avaliação IA
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <div>
            <div style={{
              background: 'linear-gradient(135deg, #1e1b4b, #312e81)',
              color: 'white',
              borderRadius: '12px',
              padding: '1.5rem 1.75rem',
              marginBottom: '2rem',
              boxShadow: '0 4px 15px rgba(49, 46, 129, 0.2)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Bot size={22} color="#818cf8" />
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
                    {briefing ? briefing.titulo : 'Briefing Estratégico de IA (Gemini 3.6 Flash)'}
                  </h3>
                  <span className="badge" style={{ background: '#4338ca', color: '#c7d2fe', fontSize: '0.75rem' }}>
                    Análise em Tempo Real
                  </span>
                </div>
                <button
                  onClick={carregarBriefingIA}
                  disabled={loadingBriefing}
                  style={{ background: 'rgba(255,255,255,0.1)', color: 'white', padding: '0.4rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  <RefreshCw size={12} className={loadingBriefing ? 'animate-spin' : ''} />
                  {loadingBriefing ? 'Gerando Análise com Gemini...' : 'Recalcular Briefing'}
                </button>
              </div>

              <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#e0e7ff', marginBottom: '1.25rem' }}>
                {briefing ? briefing.resumo_executivo : 'Carregando análise estratégica do mix de produtos e tendências da sua loja...'}
              </p>

              {briefing && (briefing.pontos_atencao?.length > 0 || briefing.oportunidades?.length > 0) && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.15)' }}>
                  <div>
                    <h5 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: '#fca5a5', fontWeight: 700, marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <AlertTriangle size={14} /> Pontos de Atenção no Estoque
                    </h5>
                    {briefing.pontos_atencao?.map((p, idx) => (
                      <div key={idx} style={{ fontSize: '0.85rem', color: '#fecaca', marginBottom: '0.2rem' }}>• {p}</div>
                    ))}
                  </div>
                  <div>
                    <h5 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: '#86efac', fontWeight: 700, marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Zap size={14} /> Oportunidades de Compra
                    </h5>
                    {briefing.oportunidades?.map((o, idx) => (
                      <div key={idx} style={{ fontSize: '0.85rem', color: '#bbf7d0', marginBottom: '0.2rem' }}>• {o}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="kpi-grid">
              <div className="kpi-card">
                <div>
                  <div className="kpi-label">Produtos Cadastrados</div>
                  <div className="kpi-value">{kpis ? kpis.total_produtos : produtos.length}</div>
                </div>
                <div className="kpi-icon-wrapper icon-blue">
                  <Package size={24} />
                </div>
              </div>

              <div className="kpi-card">
                <div>
                  <div className="kpi-label">Tendências Mapeadas</div>
                  <div className="kpi-value">{kpis ? kpis.total_tendencias : tendencias.length}</div>
                </div>
                <div className="kpi-icon-wrapper icon-emerald">
                  <TrendingUp size={24} />
                </div>
              </div>

              <div className="kpi-card">
                <div>
                  <div className="kpi-label">Estoque Crítico (Abaixo do Mínimo)</div>
                  <div className="kpi-value" style={{ color: (kpis && kpis.produtos_estoque_critico > 0) ? '#dc2626' : '#0f172a' }}>
                    {kpis ? kpis.produtos_estoque_critico : 0}
                  </div>
                </div>
                <div className="kpi-icon-wrapper icon-amber">
                  <AlertTriangle size={24} />
                </div>
              </div>

              <div className="kpi-card">
                <div>
                  <div className="kpi-label">Recomendações Geradas por IA</div>
                  <div className="kpi-value">{kpis ? kpis.total_recomendacoes : recomendacoes.length}</div>
                </div>
                <div className="kpi-icon-wrapper icon-purple">
                  <Sparkles size={24} />
                </div>
              </div>
            </div>

            <div className="dashboard-columns">
              <div className="panel-card">
                <h2 className="panel-title">
                  <TrendingUp size={20} color="#2563eb" /> Top Tendências em Evidência
                </h2>
                <div>
                  {kpis && kpis.top_tendencias && kpis.top_tendencias.map((item) => (
                    <div key={item.id} className="trend-item">
                      <div className="trend-header">
                        <span className="trend-name">{item.termo}</span>
                        <span className="trend-score">{item.score} / 100</span>
                      </div>
                      <div className="progress-track">
                        <div className="progress-fill" style={{ width: `${item.score}%` }} />
                      </div>
                      <div className="trend-meta">
                        <span><strong>Categoria:</strong> {item.categoria}</span>
                        <span>•</span>
                        <span><strong>Sazonalidade:</strong> {item.sazonalidade || 'Atemporal'}</span>
                        <span>•</span>
                        <span className={`badge badge-risk-${item.risco.toLowerCase()}`}>
                          Risco: {item.risco}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel-card">
                <h2 className="panel-title">
                  <Layers size={20} color="#d97706" /> Distribuição por Risco de Estoque
                </h2>
                <div style={{ marginTop: '1rem' }}>
                  <div className="risk-row">
                    <div className="risk-label">
                      <span className="badge badge-risk-baixo">Baixo Risco</span>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Alta procura e giro seguro</span>
                    </div>
                    <strong>{kpis && kpis.distribuicao_risco ? kpis.distribuicao_risco.Baixo : 0} tendências</strong>
                  </div>

                  <div className="risk-row">
                    <div className="risk-label">
                      <span className="badge badge-risk-moderado">Moderado</span>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Adoção gradual</span>
                    </div>
                    <strong>{kpis && kpis.distribuicao_risco ? kpis.distribuicao_risco.Moderado : 0} tendências</strong>
                  </div>

                  <div className="risk-row">
                    <div className="risk-label">
                      <span className="badge badge-risk-alto">Alto Risco</span>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Desaceleração de vendas</span>
                    </div>
                    <strong style={{ color: '#dc2626' }}>{kpis && kpis.distribuicao_risco ? kpis.distribuicao_risco.Alto : 0} tendências</strong>
                  </div>
                </div>

                <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Sparkles size={14} color="#2563eb" /> Inteligência Artificial Contínua
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    As análises utilizam o <strong>Google Gemini 3.6 Flash</strong> integrado ao banco vetorial ChromaDB para cruzar o mercado com o estoque da sua loja.
                  </p>
                </div>
              </div>
            </div>

            <div className="panel-card">
              <h2 className="panel-title">
                <Sparkles size={20} color="#7c3aed" /> Histórico de Análises & Recomendações por IA
              </h2>
              {recomendacoes.length === 0 ? (
                <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Nenhuma recomendação registrada ainda.</p>
              ) : (
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Título da Análise</th>
                        <th>Categoria</th>
                        <th>Ação Recomendada</th>
                        <th>Prioridade</th>
                        <th>Justificativa Explicável da IA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recomendacoes.slice(0, 5).map((r) => (
                        <tr key={r.id}>
                          <td style={{ fontWeight: 600 }}>{r.titulo}</td>
                          <td>{r.categoria}</td>
                          <td>
                            <span className="badge" style={{ background: '#dbeafe', color: '#1e40af' }}>
                              {r.acao_sugerida}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${r.nivel_prioridade === 'Alta' ? 'badge-risk-alto' : 'badge-risk-moderado'}`}>
                              {r.nivel_prioridade}
                            </span>
                          </td>
                          <td style={{ fontSize: '0.825rem', color: '#475569', maxWidth: '400px' }}>
                            {r.justificativa}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'rag' && (
          <div className="rag-layout">
            <div className="panel-card">
              <h2 className="panel-title">
                <Brain size={22} color="#2563eb" /> Consultor Virtual de Compras & Tendências
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1.25rem' }}>
                O modelo RAG com Gemini 3.6 Flash cruza dados de desfiles, e-commerce e redes sociais com o estoque da loja para responder perguntas estratégicas de compra.
              </p>

              <div style={{ marginBottom: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Perguntas Sugeridas:
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
                  {perguntasExemplo.map((ex, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setRagPergunta(ex.texto);
                        setRagCategoria(ex.cat);
                        executarConsultaRAG(ex.texto, ex.cat);
                      }}
                      style={{
                        textAlign: 'left',
                        padding: '0.5rem 0.75rem',
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '0.825rem',
                        color: '#334155',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}
                    >
                      <span>{ex.texto}</span>
                      <ArrowRight size={14} color="#2563eb" />
                    </button>
                  ))}
                </div>
              </div>

              <div className="rag-form-group">
                <label>Sua Dúvida de Compra ou Tendência:</label>
                <textarea
                  className="rag-textarea"
                  rows={4}
                  placeholder="Ex: Vale a pena comprar 30 unidades de camisa de linho para o final de ano?"
                  value={ragPergunta}
                  onChange={(e) => setRagPergunta(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="rag-form-group">
                  <label>Filtrar Categoria:</label>
                  <select
                    className="rag-select"
                    value={ragCategoria}
                    onChange={(e) => setRagCategoria(e.target.value)}
                  >
                    <option value="">Todas as Categorias</option>
                    <option value="Camisas">Camisas</option>
                    <option value="Calças">Calças</option>
                    <option value="Camisetas">Camisetas</option>
                    <option value="Calçados">Calçados</option>
                    <option value="Bermudas">Bermudas</option>
                    <option value="Jaquetas">Jaquetas</option>
                  </select>
                </div>

                <div className="rag-form-group">
                  <label>Vincular a Produto da Loja:</label>
                  <select
                    className="rag-select"
                    value={ragProdutoId}
                    onChange={(e) => setRagProdutoId(e.target.value)}
                  >
                    <option value="">Nenhum (Análise Geral de Mercado)</option>
                    {produtos.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nome} (Estoque: {p.quantidade_estoque})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="button"
                className="btn-primary"
                disabled={ragLoading || !ragPergunta.trim()}
                onClick={() => executarConsultaRAG()}
              >
                {ragLoading ? (
                  <>
                    <RefreshCw className="animate-spin" size={18} />
                    Consultando Gemini 3.6 Flash & ChromaDB...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Analisar Decisão com IA
                  </>
                )}
              </button>
            </div>

            <div>
              {ragResultado ? (
                <div className="rag-result-box">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <span className="badge" style={{ background: '#ede9fe', color: '#6d28d9', marginBottom: '0.4rem' }}>
                        Recomendação Explicável por IA
                      </span>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>
                        {ragResultado.pergunta}
                      </h3>
                    </div>
                    <span className={`badge badge-risk-${ragResultado.nivel_risco.toLowerCase()}`} style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                      Risco: {ragResultado.nivel_risco}
                    </span>
                  </div>

                  <div className={`action-highlight-box ${
                    ragResultado.nivel_risco === 'Alto' ? 'action-danger' : 
                    ragResultado.nivel_risco === 'Baixo' ? 'action-success' : ''
                  }`}>
                    <div className="action-title">Ação Recomendada pela IA ao Lojista</div>
                    <div className="action-value">{ragResultado.acao_recomendada}</div>
                  </div>

                  <div style={{ marginBottom: '1.25rem' }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>
                      Diagnóstico de Mercado:
                    </h4>
                    <p style={{ fontSize: '0.925rem', color: '#1e293b', lineHeight: 1.6 }}>
                      {ragResultado.diagnostico}
                    </p>
                  </div>

                  <div className="explanation-section">
                    <div className="explanation-title">
                      <HelpCircle size={18} color="#2563eb" /> Justificativa Explicável (Por que tomar esta decisão?)
                    </div>
                    <p style={{ fontSize: '0.875rem', color: '#334155', lineHeight: 1.6 }}>
                      {ragResultado.justificativa_explicavel}
                    </p>

                    {ragResultado.fontes_consultadas && ragResultado.fontes_consultadas.length > 0 && (
                      <div style={{ marginTop: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
                          Fontes e Evidências Mapeadas:
                        </span>
                        <div className="sources-tags">
                          {ragResultado.fontes_consultadas.map((f, i) => (
                            <span key={i} className="source-tag">{f}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="panel-card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem', color: '#64748b' }}>
                  <Brain size={48} color="#cbd5e1" style={{ margin: '0 auto 1rem auto' }} />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#475569', marginBottom: '0.5rem' }}>
                    Nenhuma Análise Ativa
                  </h3>
                  <p style={{ fontSize: '0.85rem', maxWidth: '380px', margin: '0 auto' }}>
                    Escolha uma pergunta sugerida ao lado ou digite sua dúvida sobre compras para receber a recomendação contextualizada com explicabilidade.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tendencias' && (
          <div className="panel-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 className="panel-title" style={{ marginBottom: '0.25rem' }}>
                  <TrendingUp size={22} color="#2563eb" /> Base de Tendências de Moda Masculina
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                  Pesquisadas e indexadas no ChromaDB com apoio contínuo do Google Gemini.
                </p>
              </div>

              <button
                type="button"
                className="badge"
                style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', color: 'white', padding: '0.65rem 1.2rem', fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                onClick={() => setModalGerarTendencia(true)}
              >
                <Sparkles size={16} /> Descobrir Novas Tendências com IA
              </button>
            </div>

            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Termo / Tendência</th>
                    <th>Categoria</th>
                    <th>Score Relevância</th>
                    <th>Nível de Risco</th>
                    <th>Sazonalidade</th>
                    <th>Fonte</th>
                    <th>Contexto de Mercado</th>
                  </tr>
                </thead>
                <tbody>
                  {tendencias.map((t) => (
                    <tr key={t.id}>
                      <td style={{ fontWeight: 600, color: '#0f172a' }}>{t.termo}</td>
                      <td>
                        <span className="badge" style={{ background: '#f1f5f9', color: '#334155' }}>
                          {t.categoria}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontWeight: 700, color: '#2563eb' }}>{t.score_relevancia}</span>
                          <div style={{ width: '60px', height: '6px', background: '#e2e8f0', borderRadius: '4px' }}>
                            <div style={{ width: `${t.score_relevancia}%`, height: '100%', background: '#3b82f6', borderRadius: '4px' }} />
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`badge badge-risk-${t.nivel_risco.toLowerCase()}`}>
                          {t.nivel_risco}
                        </span>
                      </td>
                      <td>{t.sazonalidade || 'Atemporal'}</td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{t.fonte}</td>
                      <td style={{ fontSize: '0.825rem', color: '#475569', maxWidth: '350px' }}>
                        {t.descricao}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {modalGerarTendencia && (
              <div style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60
              }}>
                <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', maxWidth: '520px', width: '90%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <Sparkles size={22} color="#4f46e5" />
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Gerar Tendências com Gemini AI</h3>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1.25rem' }}>
                    O Gemini analisará relatórios de estilo globais e gerará automaticamente novas tendências estruturadas com pontuação de risco e relevância, salvando-as no PostgreSQL e indexando no ChromaDB.
                  </p>

                  <div className="rag-form-group">
                    <label>Tema ou Foco de Pesquisa:</label>
                    <input
                      className="rag-input"
                      value={temaIA}
                      onChange={(e) => setTemaIA(e.target.value)}
                      placeholder="Ex: Alfaiataria Desestruturada, Verão 2026, Calçados Urbanos"
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                    <button
                      type="button"
                      disabled={gerandoTendenciasIA}
                      onClick={() => setModalGerarTendencia(false)}
                      style={{ padding: '0.6rem 1.25rem', borderRadius: '6px', background: '#f1f5f9', color: '#475569', fontWeight: 600 }}
                    >
                      Cancelar
                    </button>
                    <button
                      type="button"
                      disabled={gerandoTendenciasIA || !temaIA.trim()}
                      onClick={gerarTendenciasComIA}
                      style={{ padding: '0.6rem 1.25rem', borderRadius: '6px', background: '#4f46e5', color: 'white', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      {gerandoTendenciasIA ? (
                        <>
                          <RefreshCw className="animate-spin" size={16} /> Pesquisando com Gemini...
                        </>
                      ) : (
                        <>
                          <Sparkles size={16} /> Gerar e Indexar
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'produtos' && (
          <div className="panel-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 className="panel-title" style={{ marginBottom: '0.25rem' }}>
                  <Package size={22} color="#059669" /> Catálogo da Loja & Análise Automatizada por IA
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                  Avalie o potencial de mercado e os riscos de cada produto com um clique no botão <strong>Avaliar com IA</strong>.
                </p>
              </div>

              <button
                type="button"
                className="badge"
                style={{ background: '#2563eb', color: 'white', padding: '0.6rem 1rem', fontSize: '0.85rem', cursor: 'pointer' }}
                onClick={() => setModalProduto(true)}
              >
                <PlusCircle size={16} /> Novo Produto
              </button>
            </div>

            {produtos.length === 0 ? (
              <p style={{ color: '#64748b' }}>Nenhum produto cadastrado na loja.</p>
            ) : (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Produto</th>
                      <th>Categoria</th>
                      <th>Preço Venda</th>
                      <th>Estoque Atual</th>
                      <th>Estoque Mínimo</th>
                      <th>Score Tendência (IA)</th>
                      <th>Status Estoque</th>
                      <th>Ações com IA</th>
                    </tr>
                  </thead>
                  <tbody>
                    {produtos.map((p) => {
                      const estoqueCritico = p.quantidade_estoque <= p.estoque_minimo;
                      const avaliando = avaliandoProdutoId === p.id;

                      return (
                        <tr key={p.id}>
                          <td>#{p.id}</td>
                          <td style={{ fontWeight: 600 }}>{p.nome}</td>
                          <td>{p.categoria}</td>
                          <td>R$ {p.preco_medio.toFixed(2)}</td>
                          <td style={{ fontWeight: 700, color: estoqueCritico ? '#dc2626' : '#1e293b' }}>
                            {p.quantidade_estoque} un
                          </td>
                          <td>{p.estoque_minimo} un</td>
                          <td>
                            <span className="badge" style={{ background: '#ede9fe', color: '#6d28d9' }}>
                              ⭐ {p.tendencia_score} / 100
                            </span>
                          </td>
                          <td>
                            {estoqueCritico ? (
                              <span className="badge badge-risk-alto">
                                <AlertTriangle size={12} /> Crítico
                              </span>
                            ) : (
                              <span className="badge badge-risk-baixo">
                                <CheckCircle2 size={12} /> Adequado
                              </span>
                            )}
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.4rem' }}>
                              <button
                                type="button"
                                className="badge"
                                disabled={avaliando}
                                style={{ background: '#4338ca', color: 'white', cursor: 'pointer', padding: '0.4rem 0.65rem' }}
                                onClick={() => avaliarProdutoComIA(p.id)}
                              >
                                {avaliando ? (
                                  <>
                                    <RefreshCw className="animate-spin" size={12} /> Avaliando...
                                  </>
                                ) : (
                                  <>
                                    <Sparkles size={12} /> Avaliar com IA
                                  </>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {resultadoAvaliacaoIA && (
              <div style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60
              }}>
                <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', maxWidth: '580px', width: '90%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Sparkles size={22} color="#4338ca" />
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                        Avaliação Gemini: {resultadoAvaliacaoIA.produto_nome}
                      </h3>
                    </div>
                    <span className={`badge badge-risk-${resultadoAvaliacaoIA.nivel_risco?.toLowerCase()}`}>
                      Risco: {resultadoAvaliacaoIA.nivel_risco}
                    </span>
                  </div>

                  <div className="action-highlight-box">
                    <div className="action-title">Ação Recomendada pela IA</div>
                    <div className="action-value">{resultadoAvaliacaoIA.acao_recomendada}</div>
                    <div style={{ marginTop: '0.3rem', fontSize: '0.85rem', color: '#4338ca', fontWeight: 600 }}>
                      Score de Tendência Atualizado: {resultadoAvaliacaoIA.novo_score_tendencia} / 100
                    </div>
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <h5 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '0.2rem' }}>Diagnóstico de Mercado:</h5>
                    <p style={{ fontSize: '0.9rem', color: '#1e293b', lineHeight: 1.5 }}>
                      {resultadoAvaliacaoIA.diagnostico}
                    </p>
                  </div>

                  <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.5rem' }}>
                    <h5 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '0.3rem' }}>Justificativa Explicável:</h5>
                    <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: 1.5 }}>
                      {resultadoAvaliacaoIA.justificativa_explicavel}
                    </p>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      onClick={() => setResultadoAvaliacaoIA(null)}
                      style={{ padding: '0.6rem 1.5rem', borderRadius: '6px', background: '#2563eb', color: 'white', fontWeight: 600 }}
                    >
                      Entendido
                    </button>
                  </div>
                </div>
              </div>
            )}

            {modalProduto && (
              <div style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.5)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50
              }}>
                <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', maxWidth: '500px', width: '90%' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem' }}>
                    Cadastrar Produto no Estoque
                  </h3>
                  <form onSubmit={salvarNovoProduto}>
                    <div className="rag-form-group">
                      <label>Nome do Produto:</label>
                      <input
                        className="rag-input"
                        required
                        placeholder="Ex: Camiseta Oversized Algodão Heavy"
                        value={novoProd.nome}
                        onChange={(e) => setNovoProd({ ...novoProd, nome: e.target.value })}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div className="rag-form-group">
                        <label>Categoria:</label>
                        <select
                          className="rag-select"
                          value={novoProd.categoria}
                          onChange={(e) => setNovoProd({ ...novoProd, categoria: e.target.value })}
                        >
                          <option value="Camisas">Camisas</option>
                          <option value="Calças">Calças</option>
                          <option value="Camisetas">Camisetas</option>
                          <option value="Calçados">Calçados</option>
                          <option value="Bermudas">Bermudas</option>
                          <option value="Jaquetas">Jaquetas</option>
                        </select>
                      </div>

                      <div className="rag-form-group">
                        <label>Preço de Venda (R$):</label>
                        <input
                          type="number"
                          step="0.01"
                          className="rag-input"
                          required
                          value={novoProd.preco_medio}
                          onChange={(e) => setNovoProd({ ...novoProd, preco_medio: e.target.value })}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div className="rag-form-group">
                        <label>Estoque Atual:</label>
                        <input
                          type="number"
                          className="rag-input"
                          required
                          value={novoProd.quantidade_estoque}
                          onChange={(e) => setNovoProd({ ...novoProd, quantidade_estoque: e.target.value })}
                        />
                      </div>

                      <div className="rag-form-group">
                        <label>Estoque Mínimo:</label>
                        <input
                          type="number"
                          className="rag-input"
                          required
                          value={novoProd.estoque_minimo}
                          onChange={(e) => setNovoProd({ ...novoProd, estoque_minimo: e.target.value })}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                      <button
                        type="button"
                        onClick={() => setModalProduto(false)}
                        style={{ padding: '0.6rem 1.25rem', borderRadius: '6px', background: '#f1f5f9', color: '#475569', fontWeight: 600 }}
                      >
                        Cancelar
                      </button>
                      <button
                        type="submit"
                        style={{ padding: '0.6rem 1.25rem', borderRadius: '6px', background: '#2563eb', color: 'white', fontWeight: 600 }}
                      >
                        Salvar Produto
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
