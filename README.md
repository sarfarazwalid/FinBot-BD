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

# Project Structure

FinBot BD/
├── .gitignore
├── package-lock.json
├── package.json
├── README.md
├── backend/
│   ├── .gitignore
│   ├── README.md
│   ├── requirements.txt
│   ├── run_server.ps1
│   ├── app/
│   │   ├── __init__.py
│   │   ├── ambiguity.py
│   │   ├── intent_state.py
│   │   ├── main.py
│   │   ├── ood.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── version.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   └── index_pipeline.py
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py
│   │   │   ├── ragas_eval.py
│   │   │   └── README.md
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── chunker.py
│   │   │   ├── cleaner.py
│   │   │   ├── loader.py
│   │   │   ├── pipeline.py
│   │   │   ├── schemas.py
│   │   │   └── validator.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py
│   │   │   └── prompt_builder.py
│   │   └── retrieval/
│   │       ├── __init__.py
│   │       ├── bm25.py
│   │       ├── hybrid_search.py
│   │       ├── intent_detector.py
│   │       ├── query_rewriter.py
│   │       ├── rrf.py


│   │       └── vector_store.py
│   ├── data/
│   ├── scripts/
│   └── tests/
│       └── test_rag_pipeline.py
├── brand/
└── frontend/
    ├── jest.config.js
    ├── next-env.d.ts
    ├── next.config.js
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── README.md
    ├── run_dev.ps1
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── tsconfig.tsbuildinfo
    └── src/
        ├── __tests__/
        │   └── setup.ts
        ├── app/
        │   ├── globals.css
        │   ├── layout.tsx
        │   └── page.tsx
        ├── components/
        │   ├── Sidebar.tsx
        │   ├── chat/
        │   └── ui/
        ├── hooks/
        │   ├── conversation.types.ts
        │   ├── useChat.ts
        │   └── useConversations.ts
        ├── lib/
        │   ├── api.ts
        │   ├── colors.ts
        │   ├── storage.ts
        │   └── utils.ts
        └── types/
            └── index.ts

---

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
