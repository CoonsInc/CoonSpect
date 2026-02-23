import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def main():
    ollama_url = "http://localhost:11434" # временно хардкод
    qdrant_url = "qdrant"
    collection_name = "coon_knowledge_base"
    books_dir = "/app/data/"

    pdf_files = glob.glob(os.path.join(books_dir, "*.pdf")) # пока только pdf
    if not pdf_files:
        print(f"В папке {books_dir} не найдено PDF")
        return

    print(f"Найдено книг: {len(pdf_files)}")

    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    for pdf in pdf_files:
        print(f"Обработка: {os.path.basename(pdf)}...")
        loader = PyPDFLoader(pdf)
        docs = loader.load()
        
        for doc in docs:
            doc.metadata["book_title"] = os.path.basename(pdf)
        
        chunks = text_splitter.split_documents(docs)
        all_chunks.extend(chunks)

    print(f"Всего создано {len(all_chunks)} фрагментов")

    client = QdrantClient(host=qdrant_url, port=6333)
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

    print("Загрузка векторов в Qdrant...")
    QdrantVectorStore.from_documents(
        all_chunks,
        embeddings,
        url=f"http://{qdrant_url}:6333",
        collection_name=collection_name
    )
    print("База знаний загружена")

if __name__ == "__main__":
    main()
