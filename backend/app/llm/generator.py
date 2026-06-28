"""LLM answer generation using OpenRouter with offline fallback."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Set

from app.core.config import Settings
from app.ingestion.cleaner import sanitize_context
from app.llm.prompt_builder import build_prompt, detect_query_language
from app.retrieval.hybrid_search import _text_fingerprint
from app.retrieval.intent_detector import detect_intent, get_intent_anti_topics, get_intent_related_topics

logger = logging.getLogger(__name__)

_BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_BANGLISH_INDICATORS = [
    "korbo", "korar", "kore", "korun", "ki", "vabe", "er", "ache",
    "kivabe", "paben", "de", "lagen", "hobe", "asche", "gelo",
]


def _looks_like_banglish(text: str) -> bool:
    lower = text.lower()
    return any(indicator in lower for indicator in _BANGLISH_INDICATORS)


def _filter_chunks_by_language(
    chunks: List[Dict[str, Any]],
    query_lang: str,
) -> List[Dict[str, Any]]:
    if query_lang == "en":
        filtered: List[Dict[str, Any]] = []
        for chunk in chunks:
            text = chunk.get("text", "")
            has_bengali = bool(_BENGALI_RE.search(text))
            has_latin = bool(_LATIN_RE.search(text))
            # For English queries, keep chunks that are not purely Bengali.
            # Purely Bengali: has Bengali script and no Latin letters.
            if has_bengali and not has_latin:
                continue
            filtered.append(chunk)
        logger.info("Language filter (en): %d/%d chunks kept", len(filtered), len(chunks))
        return filtered
    if query_lang == "bn":
        filtered = []
        for chunk in chunks:
            text = chunk.get("text", "")
            if _BENGALI_RE.search(text):
                filtered.append(chunk)
        logger.info("Language filter (bn): %d/%d chunks kept", len(filtered), len(chunks))
        return filtered
    filtered = []
    for chunk in chunks:
        text = chunk.get("text", "")
        if _BENGALI_RE.search(text) or _looks_like_banglish(text):
            filtered.append(chunk)
    logger.info("Language filter (banglish): kept %d/%d chunks", len(filtered), len(chunks))
    return filtered if filtered else chunks


def _compress_context(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[int] = set()
    compressed: List[Dict[str, Any]] = []
    for chunk in chunks:
        text = (chunk.get("text") or "").strip()
        fp = _text_fingerprint(text)
        if fp not in seen:
            seen.add(fp)
            compressed.append(chunk)
    logger.info("Context compression: %d -> %d chunks", len(chunks), len(compressed))
    return compressed


def _compute_retrieval_confidence(chunks: List[Dict[str, Any]]) -> float:
    if not chunks:
        return 0.0
    scores = [float(chunk.get("score", 0.0) or 0.0) for chunk in chunks]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    unique_sources = len({chunk.get("source", "unknown") for chunk in chunks})
    overlap_score = min(1.0, unique_sources / max(1, len(chunks)))
    confidence = (avg_score * 0.7) + (overlap_score * 0.3)
    return round(min(0.7, max(0.0, confidence)), 3)


_client = None


def _get_client() -> Any:
    global _client

    if _client is not None:
        logger.info("[CACHE] OpenRouter client reused")
        return _client

    from openai import OpenAI

    settings = Settings()

    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing")

    _client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )

    logger.info(
        "OpenRouter client initialised (base_url=%s)",
        settings.openrouter_base_url,
    )

    return _client


def _classify_error(exc: Exception) -> str:
    error_str = str(exc).lower()
    if "api key" in error_str or "permission" in error_str or "invalid" in error_str:
        return "invalid_api_key"
    if "quota" in error_str or "rate" in error_str or "limit" in error_str:
        return "quota_exceeded"
    if "timeout" in error_str or "timed out" in error_str or "deadline" in error_str:
        return "timeout"
    if "connection" in error_str or "network" in error_str or "unreachable" in error_str:
        return "connection_failure"
    if "model" in error_str and ("not found" in error_str or "unavailable" in error_str):
        return "model_unavailable"
    return "unknown_error"


def _build_fallback_answer(
    chunks: List[Dict[str, Any]],
    query: str,
    reason: str = "",
) -> Dict[str, Any]:
    lang = detect_query_language(query)
    chunks_used = 0
    source_texts: dict[str, list[str]] = {}
    seen_texts: set[str] = set()

    for chunk in chunks:
        text = (chunk.get("text") or "").strip()
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if not sentences:
            continue
        source = chunk.get("source", "unknown")
        source_texts.setdefault(source, []).extend(sentences[:3])
        chunks_used += 1
        if sum(len(v) for v in source_texts.values()) >= 8:
            break

    if not source_texts:
        answer = "I don't have enough information to answer that."
        if reason:
            answer = f"[Service temporarily unavailable: {reason.replace('_', ' ')}] {answer}"
        logger.info("[FALLBACK] reason=%s chunks_used=0 answer_length=%d", reason, len(answer))
        return {"answer": answer, "sources": [], "confidence": 0.0}

    parts: list[str] = []
    for src, sentences in source_texts.items():
        bank_label = src.replace("_faq", "").replace("_", " ").title()
        parts.append(f"{bank_label}:")
        parts.extend(sentences[:3])
    fallback_answer = "\n".join(parts)

    if lang == "bn":
        for sentence in fallback_answer.split("\n"):
            if _BENGALI_RE.search(sentence):
                fallback_answer = sentence + "\n" + fallback_answer
                break
    elif lang == "banglish":
        pass
    else:
        fallback_answer = re.sub(r"[\u0980-\u09FF]+", "", fallback_answer).strip()

    sources = list(source_texts.keys())
    confidence = _compute_retrieval_confidence(chunks)
    logger.info(
        "[FALLBACK] reason=%s chunks_used=%d answer_length=%d sources=%s confidence=%.3f",
        reason, chunks_used, len(fallback_answer), sources, confidence,
    )
    return {"answer": fallback_answer, "sources": sources, "confidence": confidence}


def _filter_chunks_by_intent(
    chunks: List[Dict[str, Any]],
    intent: str,
    related_topics: Set[str],
    anti_topics: Set[str],
) -> List[Dict[str, Any]]:
    """Filter chunks to keep only those relevant to the detected intent."""
    if not related_topics and not anti_topics:
        return chunks

    filtered: List[Dict[str, Any]] = []
    for chunk in chunks:
        chunk_text = (chunk.get("text") or "").lower()
        chunk_source = (chunk.get("source") or "").lower()

        # For general intent or if no related topics, pass all through
        if intent == "general" or not related_topics:
            filtered.append(chunk)
            continue

        # Check for anti-topic match — exclude
        anti_match = any(anti in chunk_text for anti in anti_topics)
        if anti_match:
            logger.info("  [INTENT_FILTER] Dropping chunk (anti-topic match: %s)", anti_match)
            continue

        # Check for related topic match — include
        topic_match = any(topic in chunk_text or topic in chunk_source for topic in related_topics)
        if topic_match:
            filtered.append(chunk)
            continue

        # No match but also no anti-match: include if score is decent
        score = float(chunk.get("score", 0.0) or 0.0)
        if score >= 0.5:
            filtered.append(chunk)

    logger.info(
        "Intent filter: kept %d/%d chunks for intent=%s",
        len(filtered), len(chunks), intent,
    )
    return filtered if filtered else chunks[:3]  # Fallback: keep top 3


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def generate_answer(
    query: str,
    context: List[Dict[str, Any]],
    model: str = "",
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    timings: dict[str, float] = {}
    t_total = time.perf_counter()

    logger.info("=" * 60)
    logger.info("PIPELINE START")
    logger.info("User query: %r", query)
    logger.info("[LLM] provider=openrouter")

    lang = detect_query_language(query)
    logger.info("Detected query language: %s", lang)

    logger.info("Retrieved chunks (%d):", len(context))
    for i, c in enumerate(context, 1):
        text_preview = (c.get("text") or "")[:120].replace("\n", " ")
        logger.info("  [%d] source=%s | %s...", i, c.get("source"), text_preview)

    if not context:
        logger.info("No context -- returning default answer")
        return {
            "answer": "I don't have enough information to answer that. Please contact your bank directly.",
            "sources": [],
            "confidence": 0.0,
        }

    t0 = time.perf_counter()
    sanitized_chunks = sanitize_context(context)
    timings["sanitize"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    filtered_chunks = _filter_chunks_by_language(sanitized_chunks, lang)
    timings["lang_filter"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    compressed_chunks = _compress_context(filtered_chunks)
    timings["compress"] = (time.perf_counter() - t0) * 1000

    # NEW: Filter chunks by detected intent to avoid mixing workflows
    t0 = time.perf_counter()
    intent, intent_confidence = detect_intent(query)
    related_topics = get_intent_related_topics(intent)
    anti_topics = get_intent_anti_topics(intent)
    intent_filtered_chunks = _filter_chunks_by_intent(
        compressed_chunks, intent, related_topics, anti_topics
    )
    timings["intent_filter"] = (time.perf_counter() - t0) * 1000
    logger.info(
        "Intent filter: intent=%s confidence=%.2f | kept %d/%d chunks",
        intent, intent_confidence, len(intent_filtered_chunks), len(compressed_chunks),
    )

    t0 = time.perf_counter()
    prompt_payload = build_prompt(query, intent_filtered_chunks)
    timings["prompt"] = (time.perf_counter() - t0) * 1000

    prompt_text = prompt_payload["user"]
    prompt_chars = len(prompt_text)
    prompt_tokens = _estimate_tokens(prompt_text)
    logger.info("Prompt size: %d chars, ~%d tokens", prompt_chars, prompt_tokens)

    logger.info("Final prompt sent to OpenRouter:")
    logger.info("  System (first 300 chars): %s", prompt_payload["system"][:300])
    logger.info("  User prompt (first 500 chars): %s", prompt_payload["user"][:500])

    sources = list({chunk.get("source", "unknown") for chunk in intent_filtered_chunks})
    settings = Settings()
    model_name = model or settings.openrouter_model
    logger.info("[LLM] model=%s", model_name)

    try:
        client = _get_client()

        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt_payload["system"]},
                {"role": "user", "content": prompt_payload["user"]},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        timings["llm"] = (time.perf_counter() - t0) * 1000

        answer_text = ""
        usage = getattr(response, "usage", None)
        tokens_used = usage.total_tokens if usage else 0

        if response.choices and len(response.choices) > 0:
            answer_text = (response.choices[0].message.content or "").strip()

        if not answer_text:
            reason = _classify_error(Exception("empty_response"))
            logger.warning("OpenRouter returned empty response, using fallback")
            fallback = _build_fallback_answer(compressed_chunks, query, reason)
            total_ms = (time.perf_counter() - t_total) * 1000
            logger.info(
                "[PERF] sanitize=%.1f ms lang_filter=%.1f ms compress=%.1f ms "
                "prompt=%.1f ms llm=%.1f ms total=%.1f ms "
                "(prompt_chars=%d prompt_tokens=%d tokens_used=%d) [FALLBACK]",
                timings.get("sanitize", 0), timings.get("lang_filter", 0),
                timings.get("compress", 0), timings["prompt"],
                timings.get("llm", 0), total_ms,
                prompt_chars, prompt_tokens, tokens_used,
            )
            logger.info("[LLM] latency=%.1f ms", timings.get("llm", 0))
            logger.info("=" * 60)
            return {
                "answer": fallback["answer"],
                "sources": fallback["sources"],
                "confidence": fallback["confidence"],
            }

        confidence = min(1.0, len(answer_text) / 500.0)
        total_ms = (time.perf_counter() - t_total) * 1000
        logger.info(
            "[PERF] sanitize=%.1f ms lang_filter=%.1f ms compress=%.1f ms "
            "prompt=%.1f ms llm=%.1f ms total=%.1f ms "
            "(prompt_chars=%d prompt_tokens=%d tokens_used=%d)",
            timings.get("sanitize", 0), timings.get("lang_filter", 0),
            timings.get("compress", 0), timings["prompt"],
            timings["llm"], total_ms,
            prompt_chars, prompt_tokens, tokens_used,
        )
        logger.info("[LLM] latency=%.1f ms tokens=%d", timings["llm"], tokens_used)
        logger.info("=" * 60)

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": round(confidence, 3),
        }

    except Exception as exc:
        reason = _classify_error(exc)
        timings["llm"] = (time.perf_counter() - t0) * 1000
        logger.error("OpenRouter API call failed: %s", exc)

        fallback = _build_fallback_answer(compressed_chunks, query, reason)

        total_ms = (time.perf_counter() - t_total) * 1000
        logger.info(
            "[PERF] sanitize=%.1f ms lang_filter=%.1f ms compress=%.1f ms "
            "prompt=%.1f ms llm=%.1f ms total=%.1f ms "
            "(prompt_chars=%d prompt_tokens=%d tokens_used=%d) [FALLBACK]",
            timings.get("sanitize", 0), timings.get("lang_filter", 0),
            timings.get("compress", 0), timings.get("prompt", 0),
            timings.get("llm", 0), total_ms,
            prompt_chars, prompt_tokens, 0,
        )
        logger.info("[LLM] latency=%.1f ms", timings.get("llm", 0))
        logger.info("=" * 60)

        return {
            "answer": fallback["answer"],
            "sources": fallback["sources"],
            "confidence": fallback["confidence"],
        }