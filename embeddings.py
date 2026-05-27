"""Vector database and embedding management"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Tuple
from config import CHROMADB_PATH, MODEL_NAME

class EmbeddingManager:
    def __init__(self):
        """Initialize embedding model and vector store"""
        self.model = SentenceTransformer(MODEL_NAME)
        self.db = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb",
                persist_directory=CHROMADB_PATH,
                anonymized_telemetry=False,
            )
        )
        self.collection = None
    
    def create_collection(self, name: str = "resume_context"):
        """Create or get collection"""
        try:
            self.collection = self.db.get_collection(name)
        except:
            self.collection = self.db.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
    
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
