from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings

class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return np.array(embeddings).astype("float32")

    def get_embedding(self, text: str) -> np.ndarray:
        embedding = self.model.encode(text, show_progress_bar=False)
        return np.array(embedding).astype("float32")
