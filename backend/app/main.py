from fastapi import FastAPI
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

app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": VERSION,
    }
