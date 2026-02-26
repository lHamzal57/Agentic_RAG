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
    RAG_RETRIEVAL_EXPAND_NEIGHBORS: bool = True
    RAG_RETRIEVAL_NEIGHBOR_RADIUS: int = 1
    RAG_PROMPT_SORT_CHUNKS_BY_INDEX: bool = True

    RAG_CHUNK_SIZE: int = 1500
    RAG_CHUNK_OVERLAP: int = 150
    RAG_SEMANTIC_WINDOW_MAX_CHARS: int = 3000

    # Workflow-specific retrieval tuning
    RAG_TOP_K_GENERAL_QUESTION: int = 5
    RAG_TOP_K_SYSTEM_ARCHITECTURE: int = 8
    RAG_TOP_K_TEST_CASES: int = 6
    RAG_TOP_K_TEST_PLAN: int = 10
    RAG_TOP_K_TEST_REVIEW: int = 7


    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_GENERATE_PATH: str = "/api/generate"
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