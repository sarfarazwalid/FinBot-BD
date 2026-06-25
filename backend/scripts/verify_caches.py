#!/usr/bin/env python3
"""Verify that Pinecone client and embedding model are cached globally."""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)

from app.retrieval.vector_store import EmbeddingModel, _get_pinecone_index
from app.retrieval.hybrid_search import search

print("=== Cache Verification ===")

# Pinecone
idx1 = _get_pinecone_index()
idx2 = _get_pinecone_index()
print(f"Pinecone index cached: {idx1 is idx2}")

# Embedding model
_ = EmbeddingModel.embed("hello world")
print(f"Embedding model loaded: {EmbeddingModel._model is not None}")

print()
print("=== Search with timing ===")
search("How to reset bKash PIN?", top_k=3)