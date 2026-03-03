import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "models/gemini-flash-latest"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Base directory for persistent data
    DATA_DIR: str = os.getenv("PERSISTENT_DATA_DIR", "backend")
    
    DOCS_DIR: str = os.path.join("backend", "data", "sops")
    INDEX_DIR: str = os.path.join(DATA_DIR, "faiss_index")
    DATABASE_URL: str = f"sqlite:///./{DATA_DIR}/app.db"

    ANALYTICS_ALLOWED_EMAILS: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    PORT: int = 8000

    @property
    def allowed_emails(self) -> List[str]:
        return [e.strip() for e in self.ANALYTICS_ALLOWED_EMAILS.split(",") if e.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

