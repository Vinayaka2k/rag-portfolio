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
        
        # Check if we have relevant context
        has_context = bool(search_results) and any(score > 0.5 for _, score in search_results)
        
        if not has_context:
            # No relevant context found, return honest response
            yield "I don't have information about that in Vinayaka's portfolio. "
            yield "Feel free to ask about:\n"
            yield "- Experience and projects (especially IncidentCopilot)\n"
            yield "- Thinking patterns and mindset\n"
            yield "- Technical skills and approach to problem-solving"
            return
        
        context = "\n".join([f"- {doc}" for doc, _ in search_results])
        
        # System prompt with explicit grounding instructions
        system_prompt = """You are an AI assistant answering questions about a software engineer's portfolio, resume, and thinking patterns. 

Your job is to:
1. Provide insightful answers that showcase the person's agency, critical thinking, and impact
2. Connect their experience to broader themes like problem-solving, ownership, and innovation
3. Highlight not just what they did, but HOW they think and WHY they made decisions
4. Be direct, thoughtful, and impressive - cofounders should see someone who drives results

**CRITICAL: GROUNDING & TRUTHFULNESS**
- ONLY use information provided in the context below
- If the context doesn't contain enough detail to answer fully, say so honestly
- Do NOT speculate, assume, or hallucinate about experience not mentioned
- If asked about something outside this portfolio, politely redirect to available topics

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
