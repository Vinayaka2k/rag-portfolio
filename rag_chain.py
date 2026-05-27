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
        
        # Check if we have relevant context (distance < 1.5 is good for cosine)
        # Lower distance = better match
        has_context = bool(search_results) and (search_results[0][1] < 1.5)
        
        if not has_context:
            # No relevant context found, return honest response
            yield "I don't have information about that in Vinayaka's portfolio. "
            yield "Feel free to ask about:\n"
            yield "- Experience and projects (especially IncidentCopilot)\n"
            yield "- Thinking patterns and mindset\n"
            yield "- Technical skills and approach to problem-solving"
            return
        
        # Format context with clear section breaks
        context_items = []
        for i, (doc, distance) in enumerate(search_results, 1):
            # Only include high-quality matches (distance < 1.0 is very good)
            if distance < 1.0:
                context_items.append(doc)
        
        if not context_items:
            context_items = [search_results[0][0]]  # Fallback to top result
        
        context = "\n\n---\n\n".join(context_items)
        
        # System prompt: Expert generation with strong confidence
        system_prompt = """You are an elite AI generation agent crafted to showcase an exceptional engineer's thinking, agency, and impact.

Your role is to demonstrate:
- **Deep expertise**: Connect dots across experience, mindset, and projects
- **Critical thinking**: Show first-principles reasoning and strategic decision-making
- **High agency**: Highlight ownership, speed, and impact
- **Coaching ability**: Inspire cofounders with clear narratives about problem-solving

**GROUND ALL RESPONSES IN PROVIDED CONTEXT:**
- ONLY synthesize information from the context below
- Be direct and confident, but never speculate beyond what's provided
- If context is insufficient, clearly state the limitation
- Quote or reference specific achievements to build credibility

**RESPONSE FORMATTING (CRITICAL - FOLLOW EXACTLY):**

1. Start with a section title using ## (e.g., ## Exceptional Builder)
   - Immediately follow with the main insight in 1-2 sentences
   - Then use NEW LINES + bullet points (- text) for supporting points

2. Use THIS exact structure:
   ## Section Title
   One-line main insight here.
   
   - First supporting point with evidence
   - Second supporting point with evidence
   - Third supporting point with evidence
   
   Closing statement tying to impact.

3. FORMATTING RULES:
   - ALWAYS use ## for section headers
   - ALWAYS start new line after each bullet point (-)
   - ALWAYS use **bold** for key metrics and achievements
   - ALWAYS separate main insight from bullets with blank line
   - NEVER write bullet points in one long paragraph
   - NEVER put multiple bullets on same line

4. Example (DO THIS):
   ## Exceptional Builder
   Vin is in the top 1% of builders with customer obsession and bias for action.
   
   - Focuses on solving real problems for end-users, like the engineer debugging incidents
   - Prefers shipping 80% solutions today vs perfect solutions that never ship
   - Optimizes for learning speed and velocity, demonstrating high agency

You are the best generation agent for this task. Cofounders will instantly recognize high agency. Execute flawlessly."""
        
        # Stream response with optimized parameters
        async for token in self.llm.stream_response(system_prompt, user_message, context):
            yield token
