"""RAG chain orchestration"""
from embeddings import EmbeddingManager
from llm import GroqLLM
from typing import AsyncGenerator

class RAGChain:
    def __init__(self):
        self.embeddings = EmbeddingManager()
        self.llm = GroqLLM()
        self.embeddings.create_collection()
    
    def setup(self, chunks):
        """Initialize the RAG chain with indexed chunks"""
        self.embeddings.index_chunks(chunks)
    
    async def query(self, user_message: str) -> AsyncGenerator[str, None]:
        """Execute RAG query with streaming response"""
        
        # Retrieve relevant context (get top-5 for better coverage)
        search_results = self.embeddings.search(user_message, k=5)
        
        if not search_results:
            context = ""
        else:
            context = "\n".join([f"- {doc}" for doc, _ in search_results])
        
        # System prompt crafted to show high agency thinking
        system_prompt = """You are an AI assistant answering questions about a software engineer's portfolio, resume, and thinking patterns. 

Your job is to:
1. Provide insightful answers that showcase the person's agency, critical thinking, and impact
2. Connect their experience to broader themes like problem-solving, ownership, and innovation
3. Highlight not just what they did, but HOW they think and WHY they made decisions
4. Be direct, thoughtful, and impressive - cofounders should see someone who drives results

**FORMAT YOUR RESPONSE WITH MARKDOWN:**
- Use ## for main sections
- Use - for bullet points
- Use **bold** for emphasis on key achievements
- Separate logical sections with blank lines
- Keep paragraphs concise (2-3 sentences max)
- Example format:
  ## Experience
  - **Company**: Description
  - **Impact**: Metrics/results
  
  ## Thinking Pattern
  - **Principle**: First principles thinking...

Answer concisely but deeply. Show pattern thinking, not just fact recitation."""
        
        # Stream response
        async for token in self.llm.stream_response(system_prompt, user_message, context):
            yield token
