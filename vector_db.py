import os
from typing import Any, Dict, List, Optional

import chromadb

CHROMA_PATH = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_trends_collection():
    client = get_chroma_client()
    return client.get_or_create_collection("tendencias_moda")

def buscar_tendencias_similares(query: str, n_results: int = 3, categoria: Optional[str] = None) -> List[Dict[str, Any]]:
    collection = get_trends_collection()

    where_filter = None
    if categoria:
        where_filter = {"categoria": categoria}

    query_args = {
        "query_texts": [query],
        "n_results": n_results
    }
    if where_filter:
        query_args["where"] = where_filter

    results = collection.query(**query_args)

    docs_recuperados = []
    if results and "documents" in results and results["documents"]:
        for doc, meta, doc_id in zip(results["documents"][0], results["metadatas"][0], results["ids"][0]):
            docs_recuperados.append({
                "id": doc_id,
                "documento": doc,
                "metadados": meta
            })

    return docs_recuperados
