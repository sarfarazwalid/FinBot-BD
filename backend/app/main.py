from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.core.version import APP_NAME, DESCRIPTION, VERSION
from app.api.routes import router as chat_router

settings = Settings()

app = FastAPI(
    title=APP_NAME + " API",
    description=DESCRIPTION,
    version=VERSION,
    debug=settings.debug,
)

# CORS — allow the Next.js dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": VERSION,
    }
