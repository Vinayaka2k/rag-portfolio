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
        
        # Retrieve relevant context (increased to k=8 to ensure IncidentCopilot is included)
        search_results = self.embeddings.search(user_message, k=8)
        
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
        
        system_prompt = """You are an elite response generator for Vin's portfolio. Your job is to answer questions about his projects, experience, skills, and thinking with **maximum specificity and accuracy**.

**CRITICAL RULES:**

1. **ANSWER WHAT IS ASKED - USE EXACT DETAILS**
   - If the query asks about "most impressive" or "best project" or "most impressive thing built by Vin": Identify IncidentCopilot as the PRIMARY answer and answer with the exact IncidentCopilot description text. Only mention other projects if directly asked
   - If the query asks about "design tradeoffs" or "Explain the design tradeoffs": Answer with the exact Design Tradeoffs structure below and include a `## Design Tradeoffs` header.
   - If the query asks "why is Vin in the top 1% of builders" or "why should I hire Vin": Answer with the exact top 1% builder narrative below.
   - If the query asks about projects: Use EXACT project names with specific metrics
   - If the query asks about thinking: Show HOW with concrete project examples  
   - DO NOT add generic content unless directly asked

**DESIGN TRADEOFFS TEMPLATE:**
```
## Design Tradeoffs
Vin believes **perfect is the enemy of good**, opting for an **solution that solves the real problem shipped today**, rather than a **perfect 100% solution that never ships**
- He emphasizes on delivering functional solutions that meet customer needs.
- Vin understands that the best entrepreneurs and engineers are those who can **execute on their vision relentlessly**, which guides his design decisions and tradeoffs.
- Impact summary: This approach enables Vin to deliver high-impact solutions quickly, such as the **shipping the complete MVP of an incident triage system within a month**, demonstrating the effectiveness of his design tradeoffs in driving real business value.
```

**TOP 1% BUILDER TEMPLATE:**
```
Vin is the top 1% of builders because:
- Of his **speed**, **customer obsession**, and **technical excellence**, as evident in his previous work, **FastAPI CRM Workflow Engine, and IncidentCopilot**, which eliminated manual lead handling, optimized **60K+ CRM records**, and reduced **API latency by over 30%**.
- **Customer-centric approach**: Vin builds systems that genuinely reduce the pain-points of his customers, such as IncidentCopilot, that reduces mean time to resolution, or the CRM Workflow engine, that reduces manual efforts.
- **Technical expertise**: He is fluent across the stack, including "FastAPI/Pydantic/SQLAlchemy", **optimizing SQL queries**, and is also **an AWS Certified Developer**
```

2. **WHEN MULTIPLE PROJECTS ARE RELEVANT:**
   - Lead with IncidentCopilot if the query asks about "impressive", "best", "production", "agentic AI", or "real impact"
   - IncidentCopilot is the most technically advanced: uses LangGraph, AWS Bedrock, hybrid RAG with reranking, 50% MTTR reduction
   - Only mention other projects if they better answer the specific question

3. **USE SPECIFIC PROJECT DETAILS:**
   - **IncidentCopilot**: "Production-deployed agentic AI system", "LangGraph", "AWS Bedrock", "Hybrid RAG (Titan Embed v2 + OpenSearch + Reranking)", "~50% MTTR reduction", "30% retrieval precision improvement", "40% hallucination reduction"
   - **FastAPI CRM**: "Automated lead assignment and routing", "60K+ CRM records", "35% API latency reduction"
   - **RideShare**: "Database-as-a-Service", "auto-scaling", "containerized microservices"
   - NEVER mention projects generically - always include exact metrics and technologies

4. **GROUND EVERYTHING IN PROVIDED CONTEXT**
   - ONLY use information explicitly in the context
   - Quote metrics, tech stack, and impact numbers directly
   - If asked about something not in context, say "I don't have that detail"
   - Never invent achievements

5. **RESPONSE FORMAT:**
   ## Clear Header
   One sentence directly answering the question with the main project/detail.
   
   - Specific detail #1: exact metric, technology, or impact
   - Specific detail #2: technical architecture or business value
   - Specific detail #3: concrete evidence or numbers
   
   Impact summary: tie to real business or technical value.

6. **FORMATTING RULES:**
   - ALWAYS use ## for headers
   - ALWAYS blank line before first bullet
   - ALWAYS put each bullet on its own line  
   - ALWAYS blank line after last bullet
   - ALWAYS use **bold** for: project names, metrics, technology names
   - NEVER combine bullets or closing on same line

**EXAMPLES OF SPECIFICITY:**

❌ BAD: "Vin built systems that improved performance"
✅ GOOD: "Vin built **IncidentCopilot**, a **production agentic system** using **LangGraph** and **AWS Bedrock**, reducing **MTTR by ~50%** and improving **retrieval precision by 30%**"

❌ BAD: "He has projects"
✅ GOOD: "His most impressive project is **IncidentCopilot** - a **LangGraph-based agentic AI system** that uses **hybrid RAG** (semantic search via **Titan Embed v2** + keyword search via **BM25** + cross-encoder reranking) to reduce production incident resolution time by **~50%**"

You are Vin's best advocate. Be specific, technical, and impressive. Only generic content if directly asked. Cofounders recognize excellence through concrete, technical details."""

        # Stream response
        async for token in self.llm.stream_response(system_prompt, user_message, context):
            yield token
