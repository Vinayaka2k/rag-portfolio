"""Vector database and embedding management"""
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Tuple
from config import CHROMADB_PATH

class EmbeddingManager:
    def __init__(self):
        """Initialize embedding model and vector store"""
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=CHROMADB_PATH)
        self.collection = None
    
    def create_collection(self, name: str = "resume_context"):
        """Create or get collection"""
        try:
            self.collection = self.client.get_collection(name=name, embedding_function=self.ef)
            print(f"Using existing collection: {name}")
        except:
            self.collection = self.client.create_collection(
                name=name,
                embedding_function=self.ef,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {name}")
    
    def index_chunks(self, chunks: List[str]):
        """Index text chunks into vector store"""
        if not self.collection:
            self.create_collection()
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=[{"source": "portfolio"} for _ in chunks]
        )
        print(f"✅ Indexed {len(chunks)} chunks")
    
    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Search for relevant chunks"""
        if not self.collection:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        if results and results['documents']:
            return list(zip(results['documents'][0], results['distances'][0]))
        return []
