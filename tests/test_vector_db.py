import vector_db


def test_buscar_tendencias_similares_retorna_lista():
    resultados = vector_db.buscar_tendencias_similares(
        query="camisa de linho leve para o verão",
        n_results=2
    )
    assert isinstance(resultados, list)
    if resultados:
        primeiro = resultados[0]
        assert "documento" in primeiro
        assert "metadados" in primeiro
        assert "id" in primeiro


def test_filtro_categoria_vector_db():
    resultados = vector_db.buscar_tendencias_similares(
        query="calças",
        n_results=2,
        categoria="Calças"
    )
    assert isinstance(resultados, list)
    for r in resultados:
        assert r["metadados"].get("categoria") == "Calças"
