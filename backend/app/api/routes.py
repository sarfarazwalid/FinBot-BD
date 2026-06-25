"""Chat API routes for FinBot BD."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.llm.generator import generate_answer
from app.retrieval.hybrid_search import search as hybrid_search
from app.ambiguity import is_ambiguous_banking_query, get_clarification_message, get_clarification_options
from app.llm.prompt_builder import detect_query_language
from app.intent_state import get_pending_intent, store_pending_intent, is_bank_name, reconstruct_query

logger = logging.getLogger(__name__)

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

    answer: str = Field(..., description="Generated answer from the configured LLM")
    sources: List[str] = Field(..., description="List of source document identifiers")
    confidence: float = Field(..., description="Estimated confidence (0.0–1.0)")
    clarification_required: Optional[bool] = Field(
        None,
        description="If true, the answer is a clarification question expecting a bank name",
    )
    clarification_options: Optional[List[str]] = Field(
        None,
        description="Available options for clarification, if clarification_required is true",
    )


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_client_host(request: Request) -> str:
    """Extract client host from request, falling back to a default."""
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


def _check_pending_intent(
    message: str,
    client_host: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if there is a pending intent for this client.
    If the message is just a bank name, resolve the pending intent.
    Returns (is_resolved, resolved_query, intent).
    """
    if is_bank_name(message):
        # Check for pending intent
        pending = get_pending_intent(client_host)
        if pending is not None:
            # Resolve the intent
            bank = message.strip()
            resolved_query = reconstruct_query(
                pending["intent"],
                bank,
                pending["language"],
            )
            logger.info(
                "[CLARIFICATION_RESOLVED] bank=%s intent=%s language=%s resolved_query=%s",
                bank,
                pending["intent"],
                pending["language"],
                resolved_query,
            )
            return True, resolved_query, pending["intent"]
    return False, None, None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """Handle a chat request end-to-end.

    Pipeline:
        1. Check if there is a pending intent (user may be responding to a clarification).
        2. If pending intent, resolve it and proceed with retrieval + generation.
        3. Check for ambiguous banking queries.
        4. If ambiguous, store the intent and return clarification.
        5. Otherwise, proceed with hybrid search (BM25 + Pinecone + RRF) to retrieve context.
        6. Build prompt with retrieved chunks.
        7. Call the configured LLM provider to generate the answer.
    """
    client_host = _get_client_host(request)

    # Step 1: Check for pending intent (user responding to clarification with just a bank name)
    is_resolved, resolved_query, _ = _check_pending_intent(req.message, client_host)
    if is_resolved and resolved_query:
        # Proceed with retrieval and generation using the resolved query
        retrieved: List[Dict[str, Any]] = hybrid_search(resolved_query, top_k=5)
        result = generate_answer(resolved_query, retrieved)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            clarification_required=None,
            clarification_options=None,
        )

    # Step 2: Check for ambiguous banking queries
    is_ambiguous, intent = is_ambiguous_banking_query(req.message)
    if is_ambiguous and intent:
        language = detect_query_language(req.message)
        # Store the pending intent for this client
        store_pending_intent(client_host, intent, language, req.message)
        clarification = get_clarification_message(intent, language)
        options = get_clarification_options()
        logger.info(
            "[AMBIGUITY] intent=%s language=%s query=%s",
            intent,
            language,
            req.message,
        )
        return ChatResponse(
            answer=clarification,
            sources=[],
            confidence=0.0,
            clarification_required=True,
            clarification_options=options,
        )

    # Step 3: Retrieve context
    retrieved: List[Dict[str, Any]] = hybrid_search(req.message, top_k=5)

    # Step 4: Generate answer
    result = generate_answer(req.message, retrieved)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
        clarification_required=None,
        clarification_options=None,
    )
