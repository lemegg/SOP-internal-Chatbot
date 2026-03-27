import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

# Load .env explicitly from the root project directory
# Since this file is in backend/app/core/config.py, we look two levels up
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"), override=True)

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "models/gemini-1.5-flash"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Base directory for persistent data
    DATA_DIR: str = os.getenv("PERSISTENT_DATA_DIR", "backend")
    
    # Use absolute paths for the database to avoid issues with working directories
    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.abspath(os.path.join(self.DATA_DIR, "app.db"))
        return f"sqlite:///{db_path}"

    DOCS_DIR: str = os.path.join("backend", "data", "sops")
    INDEX_DIR: str = os.path.join(DATA_DIR, "faiss_index")

    TOP_K: int = 4
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    SECRET_KEY: str = "change-me-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    CLERK_SECRET_KEY: str = ""
    CLERK_ISSUER_URL: str = "" # e.g., https://clerk.your-domain.com or https://your-app.clerk.accounts.dev

    ANALYTICS_ALLOWED_EMAILS: str = "sruthi@theaffordableorganicstore.com,anurag@theaffordableorganicstore.com,shivam@theaffordableorganicstore.com"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    PORT: int = 8000
    SENTRY_DSN: str = ""

    @property
    def allowed_emails(self) -> List[str]:
        # Handle cases where multiple emails are comma-separated or space-separated
        raw_list = self.ANALYTICS_ALLOWED_EMAILS.replace(' ', ',').split(',')
        return [e.strip().lower() for e in raw_list if e.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

