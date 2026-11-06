import json
import os

import chromadb

import models
from database import SessionLocal

CHROMA_PATH = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
DATA_FILE = "./data/market_trends.json"

def carregar_dados_mercado():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def indexar_no_chromadb(trends):
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection("tendencias_moda")
    except Exception:
        pass

    collection = client.create_collection(
        name="tendencias_moda",
        metadata={"description": "Base de conhecimento semântica de tendências de moda masculina"}
    )

    documents = []
    metadatas = []
    ids = []

    for t in trends:
        texto_documento = (
            f"Tendência: {t['termo']}. Categoria: {t['categoria']}. "
            f"Estilo: {t['estilo']}. Sazonalidade: {t['sazonalidade']}. "
            f"Nível de Risco: {t['nivel_risco']}. Relevância: {t['score_relevancia']}/100. "
            f"Fonte: {t['fonte']}. "
            f"Detalhes: {t['conteudo']}"
        )
        documents.append(texto_documento)
        metadatas.append({
            "termo": t["termo"],
            "categoria": t["categoria"],
            "estilo": t["estilo"],
            "sazonalidade": t["sazonalidade"],
            "nivel_risco": t["nivel_risco"],
            "score_relevancia": float(t["score_relevancia"]),
            "fonte": t["fonte"]
        })
        ids.append(t["id"])

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Indexados {len(documents)} documentos no ChromaDB.")
    return collection

def sincronizar_com_postgresql(trends):
    db = SessionLocal()
    try:
        inseridos = 0
        for t in trends:
            existe = db.query(models.TendenciaModel).filter(models.TendenciaModel.termo == t["termo"]).first()
            if not existe:
                nova_tendencia = models.TendenciaModel(
                    termo=t["termo"],
                    categoria=t["categoria"],
                    score_relevancia=float(t["score_relevancia"]),
                    sazonalidade=t["sazonalidade"],
                    nivel_risco=t["nivel_risco"],
                    descricao=t["conteudo"],
                    fonte=t["fonte"]
                )
                db.add(nova_tendencia)
                inseridos += 1
        db.commit()
        print(f"Sincronizados {inseridos} registros com PostgreSQL.")
    finally:
        db.close()

def main():
    trends = carregar_dados_mercado()
    indexar_no_chromadb(trends)
    sincronizar_com_postgresql(trends)

if __name__ == "__main__":
    main()
