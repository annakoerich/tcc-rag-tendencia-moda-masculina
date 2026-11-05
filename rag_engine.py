import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

import models
import vector_db

# Carrega .env do mesmo diretório
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

def _extrair_texto_ia(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = []
        for item in conteudo:
            if isinstance(item, dict) and "text" in item:
                partes.append(item["text"])
            elif isinstance(item, str):
                partes.append(item)
        return "\n".join(partes)
    return str(conteudo)

def _extrair_json_resposta(texto: str) -> Optional[Any]:
    limpo = texto.strip()
    if limpo.startswith("```"):
        limpo = re.sub(r"^```(?:json)?", "", limpo).strip()
    if limpo.endswith("```"):
        limpo = limpo[:-3].strip()

    try:
        return json.loads(limpo)
    except Exception:
        # Tenta achar o array [...]
        match_arr = re.search(r"\[.*\]", limpo, re.DOTALL)
        if match_arr:
            try:
                return json.loads(match_arr.group(0))
            except Exception:
                pass
        # Tenta achar o objeto {...}
        match_obj = re.search(r"\{.*\}", limpo, re.DOTALL)
        if match_obj:
            try:
                return json.loads(match_obj.group(0))
            except Exception:
                pass
    return None

def _obter_llm():
    if GOOGLE_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                api_key=GOOGLE_API_KEY,
                max_retries=1,
                timeout=10
            )
        except Exception as e:
            print(f"[Aviso] Erro ao instanciar Gemini: {e}")

    if OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=OPENAI_API_KEY,
                max_retries=1,
                timeout=10
            )
        except Exception as e:
            print(f"[Aviso] Erro ao instanciar OpenAI: {e}")

    return None

def sintetizar_resposta_contextual(
    pergunta: str,
    documentos_recuperados: List[Dict[str, Any]],
    produto_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sintetizador heurístico de fallback caso o LLM esteja temporariamente indisponível.
    """
    if not documentos_recuperados:
        return {
            "pergunta": pergunta,
            "diagnostico": "Não foram encontradas evidências suficientes na base de conhecimento sobre o termo pesquisado.",
            "acao_recomendada": "Pesquisar Novo Termo",
            "nivel_risco": "Moderado",
            "justificativa_explicavel": "A base vetorial não retornou padrões para este item. Recomenda-se realizar uma pesquisa de mercado prévia.",
            "fontes_consultadas": []
        }

    top_doc = documentos_recuperados[0]
    meta = top_doc.get("metadados", {})
    termo = meta.get("termo", "Tendência Identificada")
    categoria = meta.get("categoria", "Geral")
    nivel_risco = meta.get("nivel_risco", "Moderado")
    score = meta.get("score_relevancia", 50.0)
    sazonalidade = meta.get("sazonalidade", "Atemporal")

    fontes = list(set([d.get("metadados", {}).get("fonte", "Pesquisa de Mercado") for d in documentos_recuperados]))
    estoque_alerta = ""
    acao = "Manter Monitoramento"

    if produto_info:
        qtd = produto_info.get("quantidade_estoque", 0)
        min_est = produto_info.get("estoque_minimo", 5)
        nome_prod = produto_info.get("nome", "")

        if score >= 80 and nivel_risco.lower() == "baixo":
            if qtd <= min_est:
                acao = "Aumentar Pedido com Urgência"
                estoque_alerta = f" O produto '{nome_prod}' está com estoque crítico ({qtd} unidades, abaixo do mínimo de {min_est}), enquanto o mercado aponta forte alta ({score}/100)."
            else:
                acao = "Reforçar Estoque"
                estoque_alerta = f" O estoque atual de '{nome_prod}' é de {qtd} unidades. Há espaço para ampliação segura do lote."
        elif nivel_risco.lower() == "alto" or score < 45:
            if qtd > min_est:
                acao = "Reduzir Estoque / Realizar Ação Promocional"
                estoque_alerta = f" ATENÇÃO: Há {qtd} unidades em estoque de '{nome_prod}', com risco de capital imobilizado devido à desaceleração da procura."
            else:
                acao = "Não Recomprar"
                estoque_alerta = f" Estoque controlado ({qtd} un), evitar novas compras deste modelo."
        else:
            acao = "Testar Lote Moderado"
            estoque_alerta = f" Manter compra fracionada de '{nome_prod}' para observar o comportamento da clientela local."
    else:
        if score >= 85 and nivel_risco.lower() == "baixo":
            acao = "Apostar na Coleção (Compra Alta)"
        elif nivel_risco.lower() == "alto":
            acao = "Evitar Aquisição em Grande Escala"
        elif score >= 70:
            acao = "Testar Pequeno Lote (5 a 10 peças)"
        else:
            acao = "Manter Compra Mínima"

    diagnostico = (
        f"A análise semântica identificou alinhamento com a tendência '{termo}' (Categoria: {categoria}, "
        f"Relevância: {score:.1f}/100, Sazonalidade: {sazonalidade}). Nível de risco mercadológico: {nivel_risco}."
    )

    detalhes_docs = " | ".join([d.get("documento", "") for d in documentos_recuperados[:2]])
    justificativa = (
        f"Com base nos relatórios de tendências ({', '.join(fontes)}), observou-se: {detalhes_docs}."
        f"{estoque_alerta} Essa decisão visa otimizar o fluxo de caixa do lojista e prevenir capital parado."
    )

    return {
        "pergunta": pergunta,
        "diagnostico": diagnostico,
        "acao_recomendada": acao,
        "nivel_risco": nivel_risco,
        "justificativa_explicavel": justificativa,
        "fontes_consultadas": fontes
    }

def executar_rag_llm(
    pergunta: str,
    documentos_recuperados: List[Dict[str, Any]],
    produto_info: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Executa a chain RAG com IA (Google Gemini ou OpenAI).
    """
    llm = _obter_llm()
    if not llm:
        return None

    contexto_textos = "\n---\n".join([d["documento"] for d in documentos_recuperados])

    info_loja = "Nenhum produto cadastrado informado."
    if produto_info:
        info_loja = (
            f"Produto: {produto_info.get('nome')}, Categoria: {produto_info.get('categoria')}, "
            f"Estoque Atual: {produto_info.get('quantidade_estoque')}, "
            f"Estoque Mínimo: {produto_info.get('estoque_minimo')}, Preço Médio: R$ {produto_info.get('preco_medio')}"
        )

    prompt_texto = f"""Você é um consultor especialista em tendências e gestão de compras para o varejo de moda masculina.
Seu objetivo é apoiar pequenos lojistas a decidirem quais produtos adquirir, fornecendo recomendações interpretáveis e explicáveis para evitar capital imobilizado e excesso de estoque.

Instruções:
1. Analise o contexto de mercado e os dados de estoque da loja abaixo.
2. Responda ESTRITAMENTE em formato JSON (sem blocos markdown adicionais) com estas 5 chaves exatas:
   "diagnostico": resumo do comportamento de mercado e da tendência.
   "acao_recomendada": ação direta e prática (ex: 'Aumentar Pedido com Urgência', 'Evitar Compra / Realizar Liquidação', 'Testar Lote Pequeno', etc.).
   "nivel_risco": exatamente 'Baixo', 'Moderado' ou 'Alto'.
   "justificativa_explicavel": explicação detalhada e fundamentada do porquê dessa recomendação, citando as tendências, dados da loja e riscos de estoque.
   "fontes_consultadas": lista com as fontes mencionadas no contexto (ex: ["WGSN", "TikTok Trends"]).

Contexto de Mercado Recuperado:
{contexto_textos}

Dados da Loja / Estoque:
{info_loja}

Pergunta do Lojista:
{pergunta}
"""
    try:
        resp = llm.invoke(prompt_texto)
        texto_resp = _extrair_texto_ia(resp.content)
        dados = _extrair_json_resposta(texto_resp)
        if isinstance(dados, dict) and "acao_recomendada" in dados:
            dados["pergunta"] = pergunta
            return dados
    except Exception as err:
        print(f"[Aviso] Falha ao invocar LLM ({err}).")

    return None

def consultar_rag(
    pergunta: str,
    categoria: Optional[str] = None,
    produto_id: Optional[int] = None,
    db: Optional[Session] = None,
    salvar_historico: bool = True
) -> Dict[str, Any]:
    """
    Função principal do motor RAG:
    1. Recupera contexto relevante no ChromaDB.
    2. Obtém dados de produto e estoque se especificado.
    3. Gera a recomendação contextual com explicabilidade (Gemini).
    4. Salva a recomendação gerada na tabela 'recomendacoes' do PostgreSQL.
    """
    docs = vector_db.buscar_tendencias_similares(query=pergunta, n_results=3, categoria=categoria)

    produto_info = None
    if produto_id and db:
        prod = db.query(models.ProdutoModel).filter(models.ProdutoModel.id == produto_id).first()
        if prod:
            produto_info = {
                "id": prod.id,
                "nome": prod.nome,
                "categoria": prod.categoria,
                "quantidade_estoque": prod.quantidade_estoque,
                "estoque_minimo": prod.estoque_minimo,
                "preco_medio": prod.preco_medio,
                "tendencia_score": prod.tendencia_score
            }

    resultado = executar_rag_llm(pergunta, docs, produto_info)
    if not resultado:
        resultado = sintetizar_resposta_contextual(pergunta, docs, produto_info)

    if salvar_historico and db:
        try:
            nova_rec = models.RecomendacaoModel(
                produto_id=produto_id,
                titulo=f"Análise: {pergunta[:80]}",
                categoria=categoria or (produto_info.get("categoria") if produto_info else "Geral"),
                acao_sugerida=resultado.get("acao_recomendada", "Monitorar"),
                justificativa=resultado.get("justificativa_explicavel", ""),
                nivel_prioridade="Alta" if resultado.get("nivel_risco") in ["Alto", "Baixo"] else "Média"
            )
            db.add(nova_rec)
            db.commit()
            resultado["recomendacao_id"] = nova_rec.id
        except Exception as err:
            print(f"[Aviso] Não foi possível salvar recomendação no banco: {err}")
            db.rollback()

    return resultado

# ================================================================
# NOVAS FUNCIONALIDADES 100% BASEADAS EM IA (GEMINI)
# ================================================================

def gerar_novas_tendencias_com_ia(tema: str = "Moda Masculina Atual", db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Usa o Gemini AI para analisar e descobrir tendências emergentes no mercado de moda masculina,
    salvando-as automaticamente no PostgreSQL e indexando no ChromaDB com embeddings!
    """
    llm = _obter_llm()
    if not llm:
        return []

    prompt = f"""Você é o mais conceituado analista de inteligência de mercado de moda masculina (estilo WGSN / Pitti Uomo).
Gere uma lista de 3 a 5 tendências mercadológicas REAIS e EMERGENTES para o segmento de moda masculina com foco no tema: '{tema}'.

Responda EXCLUSIVAMENTE em formato JSON (um array de objetos):
[
  {{
    "termo": "Nome da Tendência (ex: Camisa Polo em Tricot)",
    "categoria": "Camisas, Calças, Calçados, Bermudas, Camisetas ou Jaquetas",
    "score_relevancia": 88.5,
    "sazonalidade": "Primavera/Verão, Outono/Inverno ou Atemporal",
    "nivel_risco": "Baixo, Moderado ou Alto",
    "descricao": "Análise aprofundada de comportamento do consumidor, motivos da alta e conselho para o pequeno lojista.",
    "fonte": "Pitti Uomo / WGSN / Redes Sociais / E-commerce"
  }}
]
"""
    try:
        resp = llm.invoke(prompt)
        texto = _extrair_texto_ia(resp.content)
        lista_tendencias = _extrair_json_resposta(texto)
        if not isinstance(lista_tendencias, list):
            return []

        tendencias_criadas = []
        chroma_client = vector_db.get_trends_collection()

        for t in lista_tendencias:
            termo = t.get("termo")
            categoria = t.get("categoria", "Geral")
            score = float(t.get("score_relevancia", 75.0))
            sazonalidade = t.get("sazonalidade", "Atemporal")
            risco = t.get("nivel_risco", "Moderado")
            descricao = t.get("descricao", "")
            fonte = t.get("fonte", "Google Gemini AI Market Intelligence")

            # 1. Salva ou atualiza no PostgreSQL
            if db:
                existente = db.query(models.TendenciaModel).filter(models.TendenciaModel.termo == termo).first()
                if not existente:
                    novo_registro = models.TendenciaModel(
                        termo=termo,
                        categoria=categoria,
                        score_relevancia=score,
                        sazonalidade=sazonalidade,
                        nivel_risco=risco,
                        descricao=descricao,
                        fonte=fonte
                    )
                    db.add(novo_registro)
                    db.commit()
                    db.refresh(novo_registro)
                    t["id"] = novo_registro.id
                else:
                    t["id"] = existente.id

            # 2. Indexa no ChromaDB para enriquecer o RAG
            doc_id = f"ia_trend_{abs(hash(termo))}"
            doc_texto = (
                f"Tendência: {termo}. Categoria: {categoria}. Sazonalidade: {sazonalidade}. "
                f"Nível de Risco: {risco}. Relevância: {score}/100. Fonte: {fonte}. "
                f"Análise de Mercado IA: {descricao}"
            )
            chroma_client.add(
                documents=[doc_texto],
                metadatas=[{
                    "termo": termo,
                    "categoria": categoria,
                    "sazonalidade": sazonalidade,
                    "nivel_risco": risco,
                    "score_relevancia": score,
                    "fonte": fonte
                }],
                ids=[doc_id]
            )
            tendencias_criadas.append(t)

        return tendencias_criadas
    except Exception as e:
        print(f"[Erro] Falha ao gerar tendências com IA: {e}")
        return []

def analisar_produto_com_ia(produto_id: int, db: Session) -> Dict[str, Any]:
    """
    Avalia um produto específico da loja com Gemini AI:
    - Cruza os dados do produto com o banco vetorial ChromaDB.
    - Calcula o score_tendencia real com IA e atualiza o produto no PostgreSQL.
    - Gera recomendação fundamentada e registra no histórico.
    """
    prod = db.query(models.ProdutoModel).filter(models.ProdutoModel.id == produto_id).first()
    if not prod:
        return {"erro": "Produto não encontrado"}

    # Busca tendências semelhantes no ChromaDB
    docs = vector_db.buscar_tendencias_similares(query=f"{prod.nome} {prod.categoria}", n_results=3)
    contexto = "\n".join([d["documento"] for d in docs])

    llm = _obter_llm()
    if not llm:
        return {"erro": "LLM não configurado"}

    prompt = f"""Você é um consultor especialista em compras e inteligência de moda masculina.
Avalie o seguinte produto do lojista com base nas tendências de mercado atuais:

Produto: {prod.nome}
Categoria: {prod.categoria}
Preço Médio de Venda: R$ {prod.preco_medio}
Estoque Atual: {prod.quantidade_estoque} un
Estoque Mínimo: {prod.estoque_minimo} un

Contexto de Mercado Recuperado:
{contexto}

Responda ESTRITAMENTE em formato JSON:
{{
  "novo_score_tendencia": 85.0,
  "acao_recomendada": "Aumentar Pedido / Manter / Reduzir Pedido / Liquidar",
  "nivel_risco": "Baixo / Moderado / Alto",
  "diagnostico": "Resumo do comportamento deste produto no mercado atual.",
  "justificativa_explicavel": "Explicação detalhada relacionando o estoque ({prod.quantidade_estoque} un) com a demanda do mercado."
}}
"""
    try:
        resp = llm.invoke(prompt)
        texto = _extrair_texto_ia(resp.content)
        analise = _extrair_json_resposta(texto)

        if isinstance(analise, dict):
            # Atualiza o score do produto no banco
            novo_score = float(analise.get("novo_score_tendencia", prod.tendencia_score))
            prod.tendencia_score = novo_score

            # Registra a recomendação gerada
            nova_rec = models.RecomendacaoModel(
                produto_id=prod.id,
                titulo=f"Avaliação IA: {prod.nome}",
                categoria=prod.categoria,
                acao_sugerida=analise.get("acao_recomendada", "Monitorar"),
                justificativa=analise.get("justificativa_explicavel", ""),
                nivel_prioridade="Alta" if analise.get("nivel_risco") in ["Alto", "Baixo"] else "Média"
            )
            db.add(nova_rec)
            db.commit()
            db.refresh(prod)

            analise["produto_id"] = prod.id
            analise["produto_nome"] = prod.nome
            analise["recomendacao_id"] = nova_rec.id
            return analise
    except Exception as e:
        print(f"[Erro] Falha ao analisar produto com IA: {e}")

    return {"erro": "Falha na análise com IA"}

def gerar_briefing_executivo_ia(db: Session) -> Dict[str, Any]:
    """
    Gera um relatório executivo estratégico do momento da loja combinando
    o estoque real com as tendências globais mapeadas.
    """
    llm = _obter_llm()
    if not llm:
        return {
            "resumo_executivo": "Configure a chave de IA para gerar o briefing automático.",
            "pontos_atencao": [],
            "oportunidades": []
        }

    produtos = db.query(models.ProdutoModel).all()
    tendencias = db.query(models.TendenciaModel).order_by(models.TendenciaModel.score_relevancia.desc()).limit(6).all()

    dados_loja = [
        f"- {p.nome} ({p.categoria}): {p.quantidade_estoque} em estoque (mínimo: {p.estoque_minimo})"
        for p in produtos
    ]
    dados_tendencias = [
        f"- {t.termo} ({t.categoria}): Score {t.score_relevancia}/100, Risco: {t.nivel_risco}"
        for t in tendencias
    ]

    texto_dados_loja = "\n".join(dados_loja) if dados_loja else "Nenhum produto cadastrado"
    texto_dados_tendencias = "\n".join(dados_tendencias) if dados_tendencias else "Nenhuma tendência cadastrada"

    prompt = f"""Você é o diretor de inteligência de compras para o varejo de moda masculina.
Escreva um briefing executivo estratégico para o pequeno lojista com base nestes dados:

Produtos e Estoques da Loja:
{texto_dados_loja}

Top Tendências de Mercado Atuais:
{texto_dados_tendencias}

Responda ESTRITAMENTE em formato JSON:
{{
  "titulo": "Briefing Executivo de Mercado & Estoque",
  "resumo_executivo": "Parágrafo direto e assertivo resumindo a situação da loja e as principais oportunidades do varejo masculino hoje.",
  "pontos_atencao": ["Alerta sobre produto X ou categoria Y", "Risco de estoque em ..."],
  "oportunidades": ["Apostar em ...", "Reforçar pedidos de ..."]
}}
"""
    try:
        resp = llm.invoke(prompt)
        texto = _extrair_texto_ia(resp.content)
        dados = _extrair_json_resposta(texto)
        if isinstance(dados, dict):
            return dados
    except Exception as e:
        print(f"[Erro] Falha ao gerar briefing: {e}")

    return {
        "titulo": "Briefing Executivo",
        "resumo_executivo": "O mercado de moda masculina aponta forte busca por conforto, tecidos naturais e cortes relaxados.",
        "pontos_atencao": ["Monitore peças tradicionais ajustadas."],
        "oportunidades": ["Aposte em linho e modelagens soltas."]
    }
