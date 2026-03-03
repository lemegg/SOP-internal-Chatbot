import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
from app.core.config import settings

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict[str, Any]] = []

    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        if embeddings.shape[0] != len(metadata):
            raise ValueError("Number of embeddings and metadata items must match.")
        self.index.add(embeddings)
        self.metadata.extend(metadata)

    def search(self, query_embedding: np.ndarray, top_k: int = settings.TOP_K) -> List[Dict[str, Any]]:
        # faiss search expects 2D array [1, dimension]
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results

    def save(self, folder_path: str = settings.INDEX_DIR):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        faiss.write_index(self.index, os.path.join(folder_path, "faiss.index"))
        with open(os.path.join(folder_path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, folder_path: str = settings.INDEX_DIR):
        index_path = os.path.join(folder_path, "faiss.index")
        metadata_path = os.path.join(folder_path, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            with open(metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            raise FileNotFoundError(f"FAISS index or metadata not found at {folder_path}")
