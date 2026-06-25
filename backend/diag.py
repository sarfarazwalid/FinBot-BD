import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from app.retrieval.hybrid_search import search
results = search("How to reset bKash PIN?")
print(f"Results: {len(results)}")
for i, r in enumerate(results[:3]):
    print(f"[{i}] source={r.get('source')} score={r.get('score')} text={r.get('text')[:100]}...")