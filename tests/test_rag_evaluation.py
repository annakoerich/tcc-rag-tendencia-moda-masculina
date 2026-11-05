"""
Avaliação Quantitativa do Pipeline de RAG (Retrieval-Augmented Generation)
Projeto Moda - Católica SC (Engenharia de Software)

Métricas avaliadas:
1. Hit Rate @ K (K=3): proporção de perguntas de teste onde o documento correto foi recuperado.
2. Latência média de recuperação vetorial no ChromaDB.
3. Conformidade do schema de explicabilidade.
"""
import time

import vector_db
from rag_engine import consultar_rag

# Conjunto de teste representativo de consultas reais de lojistas
CASOS_DE_TESTE_RAG = [
    {
        "pergunta": "Vale a pena comprar camisas de linho para o verão?",
        "termo_esperado": "linho",
        "categoria_esperada": "Camisas"
    },
    {
        "pergunta": "Qual a tendência para calças largas e corte reto?",
        "termo_esperado": "wide leg",
        "categoria_esperada": "Calças"
    },
    {
        "pergunta": "Ainda compensa comprar calça jeans skinny?",
        "termo_esperado": "skinny",
        "categoria_esperada": "Calças"
    },
    {
        "pergunta": "Tênis branco minimalista em couro ainda vende bem?",
        "termo_esperado": "tênis",
        "categoria_esperada": "Calçados"
    }
]

def test_avaliacao_hit_rate_e_latencia_rag():
    acertos = 0
    total = len(CASOS_DE_TESTE_RAG)
    tempos_recuperacao = []

    # Warm-up para carregar o modelo ONNX de embeddings na memória
    vector_db.buscar_tendencias_similares("aquecimento", n_results=1)

    for caso in CASOS_DE_TESTE_RAG:
        t0 = time.time()
        docs = vector_db.buscar_tendencias_similares(
            query=caso["pergunta"],
            n_results=3
        )
        latencia_ms = (time.time() - t0) * 1000
        tempos_recuperacao.append(latencia_ms)

        # Verifica se o termo esperado aparece nos metadados ou documentos recuperados
        termos_recuperados = " ".join([d["documento"].lower() for d in docs])
        if caso["termo_esperado"].lower() in termos_recuperados:
            acertos += 1

    hit_rate = (acertos / total) * 100
    latencia_media = sum(tempos_recuperacao) / len(tempos_recuperacao)

    print("\n==========================================")
    print("RELATÓRIO DE AVALIAÇÃO DE IA / RAG:")
    print(f"Total de consultas avaliadas: {total}")
    print(f"Hit Rate @ 3: {hit_rate:.1f}%")
    print(f"Latência Média de Recuperação: {latencia_media:.2f} ms")
    print("==========================================")

    # Critérios de qualidade do pipeline de IA
    assert hit_rate >= 75.0, f"Hit rate insuficiente ({hit_rate}% < 75%)"
    assert latencia_media < 600.0, f"Latência de recuperação vetorial excessiva ({latencia_media}ms > 600ms)"


def test_schema_explicabilidade_rag():
    pergunta = "Como está a demanda por bermudas de alfaiataria?"
    resultado = consultar_rag(pergunta=pergunta, salvar_historico=False)

    # Validação rigorosa das chaves de explicabilidade
    chaves_obrigatorias = [
        "pergunta",
        "diagnostico",
        "acao_recomendada",
        "nivel_risco",
        "justificativa_explicavel",
        "fontes_consultadas"
    ]
    for chave in chaves_obrigatorias:
        assert chave in resultado, f"Chave de explicabilidade ausente: {chave}"

    assert resultado["nivel_risco"] in ["Baixo", "Moderado", "Alto"]
    assert len(resultado["justificativa_explicavel"]) > 20
