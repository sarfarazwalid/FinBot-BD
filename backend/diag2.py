import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from app.retrieval.hybrid_search import search
from app.ingestion.cleaner import sanitize_context
from app.llm.generator import _filter_chunks_by_language, _compress_context, detect_query_language, build_prompt
from app.core.config import Settings

query = "How to reset bKash PIN?"
print(f"Query: {query}")

# Step 1: Retrieval
retrieved = search(query)
print(f"Retrieved chunks: {len(retrieved)}")
for i, r in enumerate(retrieved[:3]):
    print(f"  [{i}] source={r.get('source')} score={r.get('score'):.4f} text={r.get('text')[:50]}...")

# Step 2: Sanitize
sanitized = sanitize_context(retrieved)
print(f"After sanitize: {len(sanitized)}")

# Step 3: Language filter
lang = detect_query_language(query)
print(f"Detected language: {lang}")
filtered = _filter_chunks_by_language(sanitized, lang)
print(f"After language filter: {len(filtered)}")
if len(filtered) == 0 and len(sanitized) > 0:
    print("WARNING: Language filter removed all chunks!")

# Step 4: Compression
compressed = _compress_context(filtered)
print(f"After compression: {len(compressed)}")
if len(compressed) == 0 and len(filtered) > 0:
    print("WARNING: Compression removed all chunks!")

# Step 5: Build prompt
prompt_payload = build_prompt(query, compressed)
prompt_text = prompt_payload['user']
print(f"Prompt size: {len(prompt_text)} chars")
print(f"Prompt preview: {prompt_text[:200]}...")

# Step 6: Call generate_answer (optional)
from app.llm.generator import generate_answer
result = generate_answer(query, retrieved)
print(f"Answer: {result['answer'][:100]}...")
print(f"Sources: {result['sources']}")
print(f"Confidence: {result['confidence']}")