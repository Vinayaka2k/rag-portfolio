"""Vector database and embedding management"""
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Tuple
from config import CHROMADB_PATH, MODEL_NAME

class EmbeddingManager:
    def __init__(self):
        """Initialize embedding model and vector store"""
        self.model = SentenceTransformer(MODEL_NAME)
        # Use new Chroma API
        self.client = chromadb.PersistentClient(path=CHROMADB_PATH)
        self.collection = None
    
    def create_collection(self, name: str = "resume_context"):
        """Create or get collection"""
        try:
            self.collection = self.client.get_collection(name)
            print(f"Using existing collection: {name}")
        except:
            self.collection = self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {name}")
    
    def index_chunks(self, chunks: List[str]):
        """Index text chunks into vector store"""
        if not self.collection:
            self.create_collection()
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[{"source": "portfolio"} for _ in chunks]
        )
        print(f"✅ Indexed {len(chunks)} chunks")
    
    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Search for relevant chunks"""
        if not self.collection:
            return []
        
        query_embedding = self.model.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )
        
        if results and results['documents']:
            return list(zip(results['documents'][0], results['distances'][0]))
        return []

