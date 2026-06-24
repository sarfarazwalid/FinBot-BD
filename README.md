# FinBot BD

Bilingual (Bengali / English) hybrid RAG customer support assistant for Bangladeshi banking FAQs.

## One-command development

```bash
npm install
npm run dev
```

This starts **both** services simultaneously:

| Service | URL | Label |
|---------|-----|-------|
| Backend (FastAPI) | http://localhost:8000 | `[backend]` cyan |
| Frontend (Next.js) | http://localhost:3000 | `[frontend]` green |

## Available scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start backend + frontend concurrently |
| `npm run backend` | Start FastAPI only (`uvicorn --reload :8000`) |
| `npm run frontend` | Start Next.js only (`next dev -p 3000`) |
| `npm run install:all` | Install root + frontend dependencies |
| `npm run health` | Quick check — `curl http://localhost:8000/health` |
| `npm run test` | Run all 82 backend tests |

## Getting started

1. Clone the repo.
2. Copy `backend/.env.example` → `backend/.env` and add your API keys:
   - `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com)
   - `PINECONE_API_KEY` — from [pinecone.io](https://pinecone.io)
3. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```
4. Install Node dependencies:
   ```bash
   npm run install:all
   ```
5. Start everything:
   ```bash
   npm run dev
   ```
6. Open http://localhost:3000

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # Routes (POST /api/v1/chat)
│   │   ├── core/          # Config + version
│   │   ├── ingestion/     # Loader, chunker, cleaner, pipeline
│   │   ├── retrieval/     # BM25, vector store, hybrid search
│   │   ├── llm/           # Prompt builder + Claude generator
│   │   └── evaluation/    # Custom RAG metrics
│   ├── data/raw/          # bKash/Nagad/DBBL FAQ text files
│   ├── tests/             # 82 passing tests
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/app/           # Next.js App Router
│   ├── src/components/    # Chat UI + Sidebar
│   └── package.json
└── package.json           # Root workspace scripts