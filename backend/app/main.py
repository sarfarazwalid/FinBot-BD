from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.core.version import APP_NAME, DESCRIPTION, VERSION
from app.api.routes import router as chat_router
from app.retrieval.vector_store import configure_huggingface_auth, get_hf_auth_status, EmbeddingModel, get_pinecone_status
from app.retrieval.bm25 import is_bm25_ready, CHUNKS_PATH

settings = Settings()


def _print_startup_report() -> None:
    """Lightweight startup report with profiling-style INFO logs."""
    key_present = "YES" if settings.openrouter_api_key else "NO"
    fallback_mode = "ENABLED" if not settings.openrouter_api_key else "DISABLED"
    chunks_exist = CHUNKS_PATH.exists()
    chunks_status = f"FOUND ({CHUNKS_PATH})" if chunks_exist else "MISSING (run ingestion pipeline)"

    print("=" * 48)
    print("FinBot BD Startup Report")
    print("=" * 48)
    print(f"Version:                 {VERSION}")
    print(f"Provider:                {settings.llm_provider}")
    print(f"Model:                   {settings.openrouter_model}")
    print(f"Pinecone API Key:        {'PRESENT' if settings.pinecone_api_key else 'MISSING'}")
    print(f"Pinecone Index:          {settings.pinecone_index_name}")
    print(f"OpenRouter Key Present:  {key_present}")
    print(f"Fallback Mode:           {fallback_mode}")
    print(f"")
    print(f"CORS Origins:")
    for origin in settings.backend_cors_origins:
        print(f"- {origin}")
    print(f"")
    print(f"Embedding Provider:      {settings.embedding_provider}")
    print(f"Embedding Model:         {settings.embedding_model} (remote API)")
    print(f"Embedding Dimension:     {settings.embedding_dimension}")
    print(f"Embedding Model Status:  deferred (lazy connect on first request)")
    print(f"Pinecone Status:         deferred (lazy connect on first request)")
    print(f"Corpus (chunks.json):    {chunks_status}")
    print(f"HF Auth Status:          deferred (authenticate on first request)")
    print("=" * 48)


_print_startup_report()

app = FastAPI(
    title=APP_NAME + " API",
    description=DESCRIPTION,
    version=VERSION,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "service": APP_NAME + " API",
        "status": "running",
        "version": VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    settings = Settings()
    chunks_exist = CHUNKS_PATH.exists()
    bm25_ready = is_bm25_ready()
    pinecone_status = get_pinecone_status()

    return {
        "status": "ok" if settings.openrouter_api_key and chunks_exist else "degraded",
        "service": APP_NAME,
        "version": VERSION,
        "provider": settings.llm_provider,
        "model": settings.openrouter_model,
        "openrouter_configured": bool(settings.openrouter_api_key),
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "corpus_available": chunks_exist,
        "bm25_ready": bm25_ready,
        "pinecone_index": settings.pinecone_index_name,
        "pinecone_authenticated": pinecone_status.get("authenticated", False),
        "pinecone_connected": pinecone_status.get("index_exists", False),
    }


@app.get("/debug/huggingface")
async def debug_huggingface():
    """Return Hugging Face authentication and embedding model status."""
    settings = Settings()
    auth_status = get_hf_auth_status()
    embed_info = EmbeddingModel.get_info()

    return {
        "authenticated": auth_status["authenticated"],
        "user": auth_status["user"],
        "token_present": bool(settings.hf_token),
        "cache_found": embed_info["cache_found"],
        "embedding_model": embed_info["model"],
        "embedding_dimension": embed_info["dimension"],
        "model_loaded": embed_info["model_loaded"],
    }


@app.get("/debug/pinecone")
async def debug_pinecone():
    """Return Pinecone connection status."""
    return get_pinecone_status()


@app.get("/debug/cors")
async def debug_cors():
    """Return CORS configuration."""
    return {
        "allowed_origins": settings.backend_cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
