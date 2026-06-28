# FinBot BD

> **Your Intelligent Banking Assistant**

FinBot is an AI-powered multilingual banking assistant built specifically for Bangladesh. It uses a **Hybrid Retrieval-Augmented Generation (Hybrid RAG)** pipeline to answer banking and mobile banking questions accurately while minimizing hallucinations.

It supports **English**, **বাংলা**, and **Banglish**, and currently provides assistance for services including:

* bKash
* Nagad
* Dutch-Bangla Bank (DBBL)

---

# Features

## AI & RAG

* Hybrid Retrieval-Augmented Generation (BM25 + Pinecone Vector Search)
* Reciprocal Rank Fusion (RRF)
* Intent-aware retrieval
* Fine-grained banking intent detection
* Query rewriting
* Context filtering before generation
* Topic-aware reranking
* OpenRouter LLM integration
* Automatic multi-model fallback
* Retrieval-aware confidence scoring
* Source citations
* Hallucination reduction

---

## Banking Intelligence

Supports banking operations such as:

* Send Money
* Cash In
* Cash Out
* PIN Reset
* Mobile Recharge
* Bill Payment
* Balance Check
* Mini Statement
* Bank Transfer
* Loan Information
* Account Opening
* Fixed Deposit (FD)

---

## Language Support

FinBot automatically detects the user's language.

Supported input:

* English
* বাংলা
* Banglish

Examples:

```
How to reset bKash PIN?
```

```
বিকাশ পিন রিসেট করবো কিভাবে?
```

```
bkash pin reset korbo kivabe?
```

Responses are generated in the same language as the query.

---

## Safety Features

* Out-of-domain detection
* Banking-only responses
* Ambiguity detection
* Clarification workflow
* Intent-aware chunk filtering
* Conversation isolation
* Request cancellation
* Stale response protection

---

# Tech Stack

## Backend

* Python
* FastAPI
* Pinecone
* SentenceTransformers
* Hugging Face
* OpenRouter
* BM25
* Reciprocal Rank Fusion (RRF)

## Frontend

* Next.js 14
* React
* TypeScript
* Tailwind CSS
* Framer Motion
* Radix UI
* React Markdown

---

# Architecture

```
User Query
      │
      ▼
Language Detection
      │
      ▼
Intent Detection
      │
      ▼
Query Rewriting
      │
      ▼
Hybrid Retrieval
 ├── BM25
 └── Pinecone
      │
      ▼
Reciprocal Rank Fusion
      │
      ▼
Intent-based Filtering
      │
      ▼
Prompt Builder
      │
      ▼
OpenRouter LLM
      │
      ▼
Generated Response
```

---

## 📁 Project Structure

```
FinBot/
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/                 # REST API endpoints
│   │   ├── core/                # Configuration & application settings
│   │   ├── embeddings/          # Embedding indexing pipeline
│   │   ├── evaluation/          # RAG evaluation & metrics
│   │   ├── ingestion/           # Data loading, cleaning & chunking
│   │   ├── llm/                 # Prompt engineering & LLM generation
│   │   ├── retrieval/           # Hybrid RAG retrieval pipeline
│   │   │   ├── bm25.py
│   │   │   ├── hybrid_search.py
│   │   │   ├── intent_detector.py
│   │   │   ├── query_rewriter.py
│   │   │   ├── rrf.py
│   │   │   └── vector_store.py
│   │   ├── ambiguity.py         # Ambiguous query detection
│   │   ├── intent_state.py      # Intent tracking
│   │   ├── ood.py               # Out-of-domain detection
│   │   └── main.py              # FastAPI entry point
│   ├── data/                    # Banking knowledge base
│   ├── scripts/                 # Utility scripts
│   ├── tests/                   # Backend test suite
│   └── requirements.txt
│
├── frontend/                    # Next.js frontend
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   ├── components/          # Reusable UI components
│   │   │   ├── chat/
│   │   │   └── ui/
│   │   ├── hooks/               # React hooks & conversation state
│   │   ├── lib/                 # API client, storage & utilities
│   │   ├── types/               # Shared TypeScript types
│   │   └── __tests__/           # Frontend test setup
│   ├── package.json
│   └── tailwind.config.ts
│
├── brand/                       # Brand assets (logos, icons, design files)
│
├── README.md
├── package.json                 # Root workspace scripts
└── .gitignore
```


# Installation

## Clone

```bash
git clone https://github.com/YOUR_USERNAME/FinBot.git
cd FinBot
```

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd ..
npm install
npm run install:all
```

---

## Environment Variables

Copy

```
backend/.env.example
```

to

```
backend/.env
```

Required variables:

| Variable            | Description               |
| ------------------- | ------------------------- |
| OPENROUTER_API_KEY  | OpenRouter API key        |
| OPENROUTER_MODEL    | OpenRouter model          |
| OPENROUTER_BASE_URL | OpenRouter endpoint       |
| PINECONE_API_KEY    | Pinecone API key          |
| PINECONE_INDEX_NAME | Pinecone index            |
| EMBEDDING_MODEL     | SentenceTransformer model |
| HF_TOKEN            | Hugging Face Read Token   |

---

# Running

Start both backend and frontend:

```bash
npm run dev
```

Backend

```
http://localhost:8000
```

Frontend

```
http://localhost:3000
```

---

# Available Scripts

| Script              | Description                |
| ------------------- | -------------------------- |
| npm run dev         | Start backend and frontend |
| npm run backend     | Backend only               |
| npm run frontend    | Frontend only              |
| npm run install:all | Install all dependencies   |
| npm run health      | Backend health check       |
| npm run test        | Run backend tests          |

---

# Health Check

```
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "FinBot",
  "version": "1.0.0",
  "provider": "openrouter"
}
```

---

# Current Supported Services

* bKash
* Nagad
* Dutch-Bangla Bank (DBBL)

---

# Planned Support

* BRAC Bank
* City Bank
* Eastern Bank PLC
* Islami Bank
* Bank Asia
* Prime Bank
* Mutual Trust Bank
* Standard Chartered Bangladesh

---

# Highlights

* Hybrid RAG Architecture
* Intent-aware Retrieval
* Multilingual Responses
* Natural Banglish Generation
* Automatic LLM Failover
* Retrieval Confidence Scoring
* Conversation Isolation
* Modern Next.js Interface
* Responsive UI
* Source Attribution

---

# Future Roadmap

* Admin Dashboard
* Knowledge Base Management
* Conversation Analytics
* Voice Support
* OCR Document Upload
* PDF Processing
* Streaming Responses
* User Authentication
* Feedback Learning
* Additional Banking Services

---

# License

This project is licensed under the MIT License.
