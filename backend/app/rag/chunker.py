from typing import List, Dict, Any
from app.core.config import settings

class Chunker:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc_text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        # For simplicity, we split by space (roughly tokens)
        words = doc_text.split()
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = chunk_id
            chunk_metadata["text"] = chunk_text
            
            chunks.append(chunk_metadata)
            
            start += (self.chunk_size - self.overlap)
            chunk_id += 1
            
        return chunks
