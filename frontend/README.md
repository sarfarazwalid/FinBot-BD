# FinBot BD — Premium Frontend

Production-quality Next.js chat interface for the FinBot BD bilingual banking assistant.

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide React
- React Markdown

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy `.env.example` to `.env.local` and configure:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Run the dev server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## Connecting to Backend

Ensure the FastAPI backend is running:

```bash
cd ../backend
uvicorn app.main:app --reload
```

The frontend expects the backend at `NEXT_PUBLIC_API_URL/api/v1/chat`.

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── SuggestedQuestions.tsx
│   │   └── Sidebar.tsx
│   ├── hooks/
│   │   └── useChat.ts
│   ├── lib/
│   │   └── api.ts
│   └── types/
│       └── index.ts
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── .env.example
```

## Features

- Dark fintech theme with emerald/navy/cyan palette
- Glass morphism UI components
- Animated message bubbles (Framer Motion)
- Markdown rendering for assistant answers
- Confidence indicator (High/Medium/Low)
- Source citations per answer
- Copy answer button
- Suggested questions on welcome screen
- Responsive layout (desktop sidebar + mobile drawer)
- Typing indicator while waiting for response
- Clear chat functionality
- Smooth auto-scrolling