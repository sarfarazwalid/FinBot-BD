from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "FinBot BD"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"

    # LLM (OpenRouter)
    llm_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "qwen/qwen3-8b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Embeddings
    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_dimension: int = 1024

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "finbot-bd"
    pinecone_environment: str = ""

    # Retrieval
    top_k: int = 5
    bm25_weight: float = 0.3
    semantic_weight: float = 0.7

    # Hugging Face
    hf_token: str = ""

    # Ingestion
    ingestion_exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            ".gitignore",
            ".DS_Store",
            "Thumbs.db",
            "*.json",
            "*.csv",
            "*.tsv",
            "*.log",
            "*.tmp",
        ]
    )