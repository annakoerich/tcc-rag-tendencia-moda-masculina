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
    print(f"-> Conectando ao ChromaDB em: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Recria a coleção de tendências para garantir dados atualizados
    try:
        client.delete_collection("tendencias_moda")
        print("-> Coleção anterior 'tendencias_moda' limpa.")
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
        # Texto semântico enriquecido para busca vetorial
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
    print(f"-> {len(documents)} documentos indexados com sucesso no ChromaDB!")
    return collection

def sincronizar_com_postgresql(trends):
    print("-> Sincronizando tendências estruturadas com PostgreSQL...")
    db = SessionLocal()
    try:
        inseridos = 0
        for t in trends:
            # Verifica se já existe tendência cadastrada com esse termo
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
        print(f"-> {inseridos} novas tendências salvas na tabela 'tendencias' do PostgreSQL!")
    finally:
        db.close()

def main():
    print("=== INICIANDO PIPELINE DE INGESTÃO (FASE 2) ===")
    trends = carregar_dados_mercado()
    print(f"Carregados {len(trends)} registros de '{DATA_FILE}'.")

    collection = indexar_no_chromadb(trends)
    sincronizar_com_postgresql(trends)

    print("\n=== TESTE DE CONSULTA SEMÂNTICA NO CHROMADB ===")
    query_teste = "Qual o risco de comprar calça jeans justa para a nova coleção?"
    print(f"Consulta de teste: '{query_teste}'")
    resultado = collection.query(query_texts=[query_teste], n_results=2)

    for i, (doc, meta) in enumerate(zip(resultado["documents"][0], resultado["metadatas"][0])):
        print(f"\n[Resultado {i+1}] {meta['termo']} (Risco: {meta['nivel_risco']}, Relevância: {meta['score_relevancia']})")
        print(f"Trecho recuperado: {doc}")

    print("\n=== PIPELINE DE INGESTÃO CONCLUÍDO COM SUCESSO ===")

if __name__ == "__main__":
    main()
