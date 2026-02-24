from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Q-Pros RAG Agent"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True

    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: str = "pdf,docx"

    CHROMA_PATH: str = "db/chroma"
    CHROMA_COLLECTION: str = "brd_docs"

    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 400
    RAG_CHUNK_OVERLAP: int = 50

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "tinyllama"
    OLLAMA_TEMPERATURE: float = 0.2
    OLLAMA_NUM_CTX: int = 4096
    OLLAMA_NUM_PREDICT: int = 512
    OLLAMA_TOP_K: int = 40
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_TIMEOUT_SECONDS: int = 120

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]

    @field_validator("RAG_CHUNK_OVERLAP")
    @classmethod
    def validate_overlap(cls, v: int):
        if v < 0:
            raise ValueError("RAG_CHUNK_OVERLAP must be >= 0")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()