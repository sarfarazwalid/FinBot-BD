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
| `npm run test` | Run all backend tests |

## Getting started

1. Clone the repo.
2. Copy `backend/.env.example` → `backend/.env` and add your API keys:
   - `OPENROUTER_API_KEY` — from [openrouter.ai](https://openrouter.ai)
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

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(empty)* | OpenRouter API key |
| `OPENROUTER_MODEL` | `qwen/qwen3-8b:free` | Model identifier on OpenRouter |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `PINECONE_API_KEY` | *(empty)* | Pinecone API key |
| `PINECONE_INDEX_NAME` | `finbot-bd` | Pinecone index name |
| `EMBEDDING_MODEL` | `intfloat/multilingual-e5-large` | SentenceTransformer model |
| `TOP_K` | `5` | Number of retrieval results |
| `HF_TOKEN` | *(empty)* | Hugging Face access token (see below) |

## Hugging Face Authentication

The embedding model (`intfloat/multilingual-e5-large`) is downloaded from
Hugging Face.  Without authentication you will see this warning:

```
Warning: You are sending unauthenticated requests to the HF Hub.
```

To silence the warning and get higher rate limits:

1.  Go to https://huggingface.co/settings/tokens and create a **read** token.
2.  Add it to `backend/.env`:

    ```
    HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx
    ```

3.  Restart the backend.

On startup you should see:

```
HF Token Present: YES
[CACHE] HuggingFace authenticated: YES
```

The token is **never** logged or exposed in source code.  It is only read from
`backend/.env` at runtime and forwarded to the Hugging Face SDK via
environment variables.

## Verify OpenRouter connectivity

```bash
cd backend
python -c "
import os
from openai import OpenAI
client = OpenAI(
    api_key=os.environ['OPENROUTER_API_KEY'],
    base_url=os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1') + '/chat/completions'
)
resp = client.chat.completions.create(
    model=os.environ.get('OPENROUTER_MODEL', 'qwen/qwen3-8b:free'),
    messages=[{'role': 'user', 'content': 'Say hello from OpenRouter!'}]
)
print('OpenRouter says:', resp.choices[0].message.content)
"
```

## Health check

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "ok",
  "service": "FinBot BD",
  "version": "1.0.0",
  "provider": "openrouter",
  "model": "qwen/qwen3-8b:free"
}
```

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # Routes (POST /api/v1/chat)
│   │   ├── core/          # Config + version
│   │   ├── ingestion/     # Loader, chunker, cleaner, pipeline
│   │   ├── retrieval/     # BM25, vector store, hybrid search
│   │   ├── llm/           # Prompt builder + OpenRouter generator
│   │   └── evaluation/    # Custom RAG metrics
│   ├── data/raw/          # bKash/Nagad/DBBL FAQ text files
│   ├── tests/             # Passing tests
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/app/           # Next.js App Router
│   ├── src/components/    # Chat UI + Sidebar
│   └── package.json
└── package.json           # Root workspace scripts