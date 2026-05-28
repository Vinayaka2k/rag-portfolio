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
        self.general_collection = None
        self.faq_collection = None

    def _get_or_create(self, name: str):
        """Get or create a named collection"""
        try:
            col = self.client.get_collection(
                name=name, embedding_function=self.ef
            )
            print(f"Using existing collection: {name}")
        except Exception:
            col = self.client.create_collection(
                name=name,
                embedding_function=self.ef,
                metadata={"hnsw:space": "cosine"},
            )
            print(f"Created new collection: {name}")
        return col

    def create_collections(self):
        """Create or load both collections"""
        self.general_collection = self._get_or_create("resume_context")
        self.faq_collection = self._get_or_create("faq_context")

    def _index(self, collection, chunks: List[str], id_prefix: str):
        """Index a list of chunks into a collection"""
        if not chunks:
            return
        ids = [f"{id_prefix}_{i}" for i in range(len(chunks))]
        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=[{"source": id_prefix} for _ in chunks],
        )
        print(f"✅ Indexed {len(chunks)} chunks into '{id_prefix}' collection")

    def index_general_chunks(self, chunks: List[str]):
        if not self.general_collection:
            self.create_collections()
        self._index(self.general_collection, chunks, "general")

    def index_faq_chunks(self, chunks: List[str]):
        if not self.faq_collection:
            self.create_collections()
        self._index(self.faq_collection, chunks, "faq")

    def search_faq(self, query: str, k: int = 1) -> List[Tuple[str, float]]:
        """
        Search the FAQ collection first.
        Returns the best match if distance < FAQ_THRESHOLD, else empty list.
        """
        FAQ_THRESHOLD = 0.55  # cosine distance; lower = more similar
        if not self.faq_collection:
            return []

        results = self.faq_collection.query(
            query_texts=[query],
            n_results=min(k, 3),
        )

        if results and results["documents"] and results["documents"][0]:
            pairs = list(
                zip(results["documents"][0], results["distances"][0])
            )
            pairs.sort(key=lambda x: x[1])
            # Only return if the best match is genuinely close
            if pairs[0][1] < FAQ_THRESHOLD:
                return pairs[:k]
        return []

    def search_general(
        self, query: str, k: int = 8
    ) -> List[Tuple[str, float]]:
        """Search the general (resume/mindset/projects) collection"""
        if not self.general_collection:
            return []

        results = self.general_collection.query(
            query_texts=[query],
            n_results=k,
        )

        if results and results["documents"] and results["documents"][0]:
            pairs = list(
                zip(results["documents"][0], results["distances"][0])
            )
            pairs.sort(key=lambda x: x[1])
            return pairs
        return []

    # ------------------------------------------------------------------ #
    # Backwards-compatible alias used by older code paths
    # ------------------------------------------------------------------ #
    def create_collection(self, name: str = "resume_context"):
        self.create_collections()

    def index_chunks(self, chunks: List[str]):
        self.index_general_chunks(chunks)

    def search(self, query: str, k: int = 8) -> List[Tuple[str, float]]:
        return self.search_general(query, k)
