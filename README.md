# RAG Portfolio Backend

Lightweight RAG chatbot backend for an agentic portfolio. Built with FastAPI, chromadb, and Groq LLM.

## Features

- ⚡ **Ultra-fast inference** (~150-400ms per query with Groq)
- 🔍 **Lightweight embeddings** (all-MiniLM-L6-v2, 22MB)
- 💾 **Local vector database** (SQLite + chromadb, zero external deps)
- 🚀 **Serverless-ready** (Render.com free tier)
- 📡 **Streaming responses** (real-time token streaming)
- 🎯 **RAG-powered** (retrieval-augmented generation)

## Quick Start

### 1. Install Dependencies
```bash
pip install poetry
poetry install
```

### 2. Set Up Data
Create `data/` directory with:
- `resume.txt` - Your resume
- `mindset.md` - Your thinking patterns and values
- `projects.json` - Notable projects

### 3. Configure Groq API
Get free API key at https://console.groq.com

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 4. Run Locally
```bash
python main.py
```

Visit `http://localhost:8000` to see API docs.

## API Endpoints

### GET `/health`
Health check for frontend wake-up
```bash
curl http://localhost:8000/health
```

### GET `/suggested-questions`
Pre-crafted questions to show users
```bash
curl http://localhost:8000/suggested-questions
```

### POST `/chat`
Chat with RAG streaming response
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What was your most impressive project?"}'
```

## Architecture

```
Frontend (Vercel)
    ↓ /health (on page load - warms up backend)
    ↓ /chat (streaming RAG response)
Backend (Render)
    ├─ Embeddings: all-MiniLM-L6-v2
    ├─ Vector DB: SQLite + chromadb
    └─ LLM: Groq API
```

## Deployment

### Deploy to Render.com (Free Tier)
1. Push to GitHub
2. Connect repo to Render
3. Set environment: `GROQ_API_KEY`
4. Deploy with `python main.py`

## Tech Stack

- **Framework**: FastAPI
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: chromadb
- **LLM**: Groq API
- **Deployment**: Render.com

## Performance

- Embedding search: **2ms**
- LLM inference: **100-200ms** (Groq)
- Total latency: **150-400ms**

## License

MIT
