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
        has_context = bool(search_results) and (search_results[0][1] < 1.5)
        
        if not has_context:
            yield "I don't have information about that in Vinayaka's portfolio. "
            yield "Feel free to ask about:\n"
            yield "- Experience and projects (especially IncidentCopilot)\n"
            yield "- Thinking patterns and mindset\n"
            yield "- Technical skills and approach to problem-solving"
            return
        
        # Format context with clear section breaks
        context_items = []
        for i, (doc, distance) in enumerate(search_results, 1):
            if distance < 1.0:
                context_items.append(doc)
        
        if not context_items:
            context_items = [search_results[0][0]]
        
        context = "\n\n---\n\n".join(context_items)
        
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

**RESPONSE FORMATTING (CRITICAL - MUST FOLLOW EXACTLY):**

Structure your response as:
1. A section header with ## (example: ## Most Impressive Project)
2. A single sentence summarizing the main point
3. A blank line
4. 2-3 bullet points, each on its own line, starting with "-"
5. A blank line after the last bullet
6. A closing sentence summarizing the impact

**EXACT FORMAT TO FOLLOW:**
## Section Header
Main sentence summarizing the key point.

- First supporting detail with evidence and numbers
- Second supporting detail with impact metrics
- Third supporting detail with business value

Final closing sentence that ties everything to high agency and impact.

**CRITICAL FORMATTING RULES:**
- ALWAYS put exactly ONE blank line between main sentence and first bullet
- ALWAYS put exactly ONE blank line between last bullet and closing sentence
- ALWAYS put each bullet point on its own line
- ALWAYS use **bold** for metrics, achievements, and technical concepts
- NEVER combine two bullets on the same line
- NEVER connect closing sentence to last bullet without a blank line
- Closing sentence should emphasize impact, agency, or business value

You are the best generation agent for this task. Execute with flawless formatting. Cofounders will instantly recognize Vin's high agency."""

        # Stream response
        async for token in self.llm.stream_response(system_prompt, user_message, context):
            yield token
