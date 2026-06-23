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
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"

    # LLM
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20240620"

    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "finbot-bd"
    pinecone_environment: str = ""

    # Retrieval
    top_k: int = 5
    bm25_weight: float = 0.3
    semantic_weight: float = 0.7

    # Ingestion
    ingestion_exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "README.md",
            "README",
            ".gitignore",
            ".DS_Store",
            "Thumbs.db",
            "*.json",
            "*.csv",
            "*.tsv",
            "*.log",
            "*.tmp",
            ".*",
        ]
    )
