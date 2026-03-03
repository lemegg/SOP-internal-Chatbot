from typing import List, Dict, Any
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore
from app.core.config import settings

class Retriever:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        try:
            self.vector_store.load()
        except FileNotFoundError:
            # Vector store index must be built first
            pass

    def retrieve(self, query: str, top_k: int = settings.TOP_K) -> List[Dict[str, Any]]:
        query_embedding = self.embedder.get_embedding(query)
        results = self.vector_store.search(query_embedding, top_k)
        return results
