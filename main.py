"""FastAPI application"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_loader import load_data, chunk_text, load_faq_chunks
from rag_chain import RAGChain

# Initialize FastAPI app
app = FastAPI(title="RAG Portfolio Backend", version="0.1.0")

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = None


class ChatMessage(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    model: str = "portfolio-rag"


SUGGESTED_QUESTIONS = [
    "What was your most impressive project and why?",
    "Why is Vin the top 1% of builders?",
    "How does Vin think about products?",
    "Explain Vin's multi-agentic AI experience",
    "What design tradeoffs does Vin make?",
    "What excites Vin about startups?",
]


@app.on_event("startup")
async def startup_event():
    """Initialize RAG chain on startup"""
    global rag

    print("🚀 Initializing RAG Portfolio Backend...")

    # --- General portfolio chunks (resume + mindset + projects) ---
    portfolio_data = load_data()
    general_chunks = chunk_text(portfolio_data, chunk_size=600, overlap=50)

    # --- FAQ chunks: one chunk per Q&A block ---
    faq_chunks = load_faq_chunks()
    print(f"   Loaded {len(faq_chunks)} FAQ chunks")

    if not general_chunks and not faq_chunks:
        print("⚠️  Warning: No chunks found. Using placeholder.")
        general_chunks = [
            "Portfolio data not yet loaded. "
            "Please add resume.txt, mindset.md, or projects.json to /data directory"
        ]

    rag = RAGChain()
    rag.setup(general_chunks, faq_chunks)

    total = len(general_chunks) + len(faq_chunks)
    print(f"✅ RAG Portfolio Backend ready! ({total} chunks indexed)")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


@app.get("/suggested-questions")
async def get_suggested_questions():
    return {"questions": SUGGESTED_QUESTIONS}


@app.post("/chat")
async def chat(msg: ChatMessage):
    global rag

    if not rag:
        raise HTTPException(status_code=503, detail="RAG chain not initialized")

    if not msg.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def generate():
        try:
            async for token in rag.query(msg.message):
                yield f"data: {token}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/")
async def root():
    return {
        "name": "RAG Portfolio Backend",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "suggested_questions": "/suggested-questions",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
