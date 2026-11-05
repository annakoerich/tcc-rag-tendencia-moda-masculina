from rag_engine import sintetizar_resposta_contextual


def test_sintese_sem_documentos():
    resultado = sintetizar_resposta_contextual(
        pergunta="Termo inexistente no mercado",
        documentos_recuperados=[],
        produto_info=None
    )
    assert resultado["nivel_risco"] == "Moderado"
    assert "Não foram encontradas evidências" in resultado["diagnostico"]
    assert "fontes_consultadas" in resultado


def test_sintese_com_documentos_e_estoque_critico():
    mock_docs = [{
        "id": "mock_1",
        "documento": "Tendência: Camisa de Linho. Categoria: Camisas. Relevância: 95.0/100. Risco: Baixo.",
        "metadados": {
            "termo": "Camisa de Linho",
            "categoria": "Camisas",
            "score_relevancia": 95.0,
            "nivel_risco": "Baixo",
            "sazonalidade": "Primavera/Verão",
            "fonte": "WGSN 2026"
        }
    }]
    mock_produto = {
        "id": 1,
        "nome": "Camisa de Linho Branca",
        "categoria": "Camisas",
        "quantidade_estoque": 2,
        "estoque_minimo": 5,
        "preco_medio": 180.0
    }

    resultado = sintetizar_resposta_contextual(
        pergunta="Devo comprar camisa de linho?",
        documentos_recuperados=mock_docs,
        produto_info=mock_produto
    )

    assert "Aumentar Pedido com Urgência" in resultado["acao_recomendada"]
    assert resultado["nivel_risco"] == "Baixo"
    assert "WGSN 2026" in resultado["fontes_consultadas"]
    assert "estoque crítico" in resultado["justificativa_explicavel"].lower()


def test_sintese_com_risco_alto_e_excesso_estoque():
    mock_docs = [{
        "id": "mock_2",
        "documento": "Tendência: Calça Skinny em Queda. Relevância: 30.0/100. Risco: Alto.",
        "metadados": {
            "termo": "Calça Jeans Skinny",
            "categoria": "Calças",
            "score_relevancia": 30.0,
            "nivel_risco": "Alto",
            "sazonalidade": "Atemporal",
            "fonte": "Relatório Varejo"
        }
    }]
    mock_produto = {
        "id": 2,
        "nome": "Calça Skinny Rasgada",
        "categoria": "Calças",
        "quantidade_estoque": 25,
        "estoque_minimo": 5,
        "preco_medio": 150.0
    }

    resultado = sintetizar_resposta_contextual(
        pergunta="Devo renovar calças skinny?",
        documentos_recuperados=mock_docs,
        produto_info=mock_produto
    )

    assert "Reduzir Estoque" in resultado["acao_recomendada"]
    assert resultado["nivel_risco"] == "Alto"
    assert "capital imobilizado" in resultado["justificativa_explicavel"].lower()
