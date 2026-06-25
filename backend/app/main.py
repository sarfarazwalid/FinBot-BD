from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.core.version import APP_NAME, DESCRIPTION, VERSION
from app.api.routes import router as chat_router
from app.retrieval.vector_store import configure_huggingface_auth, get_hf_auth_status, EmbeddingModel

settings = Settings()


def _print_startup_report() -> None:
    key_present = "YES" if settings.openrouter_api_key else "NO"
    fallback_mode = "ENABLED" if not settings.openrouter_api_key else "DISABLED"

    # Authenticate Hugging Face and get status
    hf_result = configure_huggingface_auth()
    hf_auth = "Authenticated" if hf_result["authenticated"] else "Not Authenticated"
    hf_user = hf_result["user"] if hf_result["user"] else "N/A"

    # Check embedding cache status
    embed_info = EmbeddingModel.get_info()
    cache_status = "Found" if embed_info["cache_found"] else "Not Checked"

    print("=" * 48)
    print("FinBot BD Startup Report")
    print("=" * 48)
    print(f"Version:                 {VERSION}")
    print(f"Provider:                {settings.llm_provider}")
    print(f"Model:                   {settings.openrouter_model}")
    print(f"Pinecone Index:          {settings.pinecone_index_name}")
    print(f"OpenRouter Key Present:  {key_present}")
    print(f"Fallback Mode:           {fallback_mode}")
    print(f"")
    print(f"HF Auth:                 {hf_auth}")
    print(f"HF User:                 {hf_user}")
    print(f"Embedding Model:         {settings.embedding_model}")
    print(f"Embedding Cache:         {cache_status}")
    print(f"Embedding Dimension:     {settings.embedding_dimension}")
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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    settings = Settings()
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": VERSION,
        "provider": settings.llm_provider,
        "model": settings.openrouter_model,
        "fallback_mode": not bool(settings.openrouter_api_key),
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