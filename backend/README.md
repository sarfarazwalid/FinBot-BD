# FinBot BD

A bilingual (Bengali & English) RAG-powered banking customer support assistant for Bangladesh, covering DBBL, bKash, and Nagad queries.

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Configuration and core utilities
│   ├── ingestion/     # Data loading and chunking
│   ├── retrieval/     # Vector store and BM25 retrieval
│   ├── llm/           # LLM generation and prompts
│   ├── evaluation/    # Evaluation metrics and testing
│   └── main.py        # FastAPI application entrypoint
├── data/
│   ├── raw/           # Raw documents and PDFs
│   └── processed/     # Chunked and indexed data
├── scripts/           # Utility and maintenance scripts
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Getting Started

1. Clone the repository
2. Navigate to the `backend` directory
3. Copy `.env.example` to `.env` and fill in your API keys
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`

## Endpoints

- `GET /health` - Health check

## Tech Stack

- FastAPI
- Python 3.12
- Pinecone (Dimension: 1024, Metric: cosine)
- Anthropic Claude API
- sentence-transformers (`intfloat/multilingual-e5-large`)
- rank-bm25
- Pydantic Settings
- python-dotenv

## Embeddings

The system uses `intfloat/multilingual-e5-large` as the embedding model. This model:

- Generates 1024-dimensional vectors, optimized for multilingual semantic retrieval
- Supports Bengali, English, and Banglish (Romanized Bengali) — critical for the FinBot BD domain
- Handles banking-specific terminology across bKash, DBBL, and Nagad queries
- Provides improved retrieval accuracy over the smaller e5-base variant (384 → 1024 dimensions)

> **Interview talking point:** *multilingual-e5-large provides improved multilingual semantic retrieval for Bengali, English, and Banglish banking queries. The 1024-dimension vectors capture richer semantic relationships, which is essential when users ask the same question in multiple scripts (e.g., "PIN ভুলে গেছি", "amar pin vule gechi", "I forgot my PIN").*
