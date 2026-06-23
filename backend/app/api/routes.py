"""Chat API routes for FinBot BD."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.llm.generator import generate_answer
from app.retrieval.hybrid_search import search as hybrid_search

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Incoming chat message from the client."""

    message: str = Field(..., description="User's banking query", min_length=1)


class SourceRef(BaseModel):
    """Reference to a source document used in the answer."""

    source: str = Field(..., description="Source identifier (e.g. 'bkash_faq')")


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    answer: str = Field(..., description="Generated answer from Claude")
    sources: List[str] = Field(..., description="List of source document identifiers")
    confidence: float = Field(..., description="Estimated confidence (0.0–1.0)")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Handle a chat request end-to-end.

    Pipeline:
        1. Hybrid search (BM25 + Pinecone + RRF) to retrieve context.
        2. Build prompt with retrieved chunks.
        3. Call Claude Sonnet to generate the answer.
    """
    # 1. Retrieve context
    retrieved: List[Dict[str, Any]] = hybrid_search(req.message, top_k=5)

    # 2. Generate answer
    result = generate_answer(req.message, retrieved)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
    )