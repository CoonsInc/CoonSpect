import os
import glob
import re
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

def clean_text(text: str) -> str:
    """Очистка текста от мусора PDF"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    return text.strip()

def main():
    ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    qdrant_url = "qdrant"
    collection_name = "coon_knowledge_base"
    books_dir = "/app/data/"

    pdf_files = glob.glob(os.path.join(books_dir, "*.pdf"))
    if not pdf_files:
        print(f"В папке {books_dir} не найдено PDF")
        return

    embeddings_model = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
    client = QdrantClient(host=qdrant_url, port=6333)

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    for pdf in pdf_files:
        file_name = os.path.basename(pdf)
        print(f"Обработка книги: {file_name}...")
        loader = PyPDFLoader(pdf)
        pages = loader.load()
        
        book_chunks_data = []
        for page in pages:
            cleaned_content = clean_text(page.page_content)
            chunks = text_splitter.split_text(cleaned_content)
            
            for chunk_txt in chunks:
                book_chunks_data.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk_txt,
                    "page": page.metadata.get("page", 0) + 1
                })

        points = []
        print(f"Создание эмбеддингов для {len(book_chunks_data)} чанков...")
        
        for i, chunk in enumerate(book_chunks_data):
            payload = {
                "page_content": chunk["text"],
                "metadata": {
                    "book_title": file_name,
                    "page": chunk["page"],
                    "prev_id": book_chunks_data[i-1]["id"] if i > 0 else None,
                    "next_id": book_chunks_data[i+1]["id"] if i < len(book_chunks_data)-1 else None
                }
            }
            
            vector = embeddings_model.embed_query(chunk["text"])
            points.append(PointStruct(id=chunk["id"], vector=vector, payload=payload))

        for j in range(0, len(points), 50):
            client.upsert(collection_name=collection_name, points=points[j:j+50])
            
    print("База знаний успешно загружена")

if __name__ == "__main__":
    main()
