"""FastAPI application"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from pathlib import Path

from data_loader import load_data, chunk_text
from rag_chain import RAGChain

# Initialize FastAPI app
app = FastAPI(title="RAG Portfolio Backend", version="0.1.0")

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG chain (lazy loaded on startup)
rag = None

# Models
class ChatMessage(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    model: str = "portfolio-rag"

# Pre-defined suggested questions
SUGGESTED_QUESTIONS = [
    "What was your most impressive project and why?",
    "How do you approach problem-solving?",
    "Tell me about your leadership philosophy",
    "What's your take on building products with high agency?",
    "Describe a time you had to make a hard technical decision",
    "What excites you about startup environments?"
]

@app.on_event("startup")
async def startup_event():
    """Initialize RAG chain on startup"""
    global rag
    
    print("🚀 Initializing RAG Portfolio Backend...")
    
    # Load and chunk data
    portfolio_data = load_data()
    chunks = chunk_text(portfolio_data, chunk_size=600, overlap=50)  # Optimized for better retrieval
    
    if not chunks:
        print("⚠️ Warning: No chunks found. Using sample data.")
        chunks = ["Portfolio data not yet loaded. Please add resume.txt, mindset.md, or projects.json to /data directory"]
    
    # Initialize RAG chain
    rag = RAGChain()
    rag.setup(chunks)
    
    print(f"✅ RAG Portfolio Backend ready! ({len(chunks)} chunks indexed)")

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for frontend wake-up"""
    return HealthResponse(status="healthy")

@app.get("/suggested-questions")
async def get_suggested_questions():
    """Return pre-crafted questions to prompt users"""
    return {"questions": SUGGESTED_QUESTIONS}

@app.post("/chat")
async def chat(msg: ChatMessage):
    """Chat endpoint with streaming RAG response"""
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
    """Root endpoint"""
    return {
        "name": "RAG Portfolio Backend",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "suggested_questions": "/suggested-questions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
