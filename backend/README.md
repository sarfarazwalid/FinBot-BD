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
- Pinecone
- Anthropic Claude API
- sentence-transformers
- rank-bm25
- Pydantic Settings
- python-dotenv