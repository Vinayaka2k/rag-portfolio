"""RAG chain orchestration"""
from embeddings import EmbeddingManager
from llm import GroqLLM
from typing import AsyncGenerator, List, Tuple


class RAGChain:
    def __init__(self):
        self.embeddings = EmbeddingManager()
        self.llm = GroqLLM()
        self.embeddings.create_collections()

    def setup(self, general_chunks: List[str], faq_chunks: List[str] = None):
        """Index both general and FAQ chunks"""
        self.embeddings.index_general_chunks(general_chunks)
        if faq_chunks:
            self.embeddings.index_faq_chunks(faq_chunks)

    # ------------------------------------------------------------------ #
    # Core query pipeline
    # ------------------------------------------------------------------ #

    async def query(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Retrieval priority:
          1. FAQ collection  — if a close match exists (distance < 0.55),
             the answer is already written; the LLM only lightly formats it.
          2. General collection — resume / mindset / projects chunks.
             The LLM synthesises an answer from the retrieved context.
        """

        # ── Step 1: try FAQ first ───────────────────────────────────────
        faq_results = self.embeddings.search_faq(user_message, k=1)

        if faq_results:
            faq_doc, faq_distance = faq_results[0]
            async for token in self._stream_faq_response(
                user_message, faq_doc
            ):
                yield token
            return

        # ── Step 2: fall back to general retrieval ─────────────────────
        general_results = self.embeddings.search_general(user_message, k=8)

        has_context = bool(general_results) and general_results[0][1] < 1.5
        if not has_context:
            yield "I don't have information about that in Vinayaka's portfolio. "
            yield "Feel free to ask about:\n"
            yield "- His projects (IncidentCopilot, FastAPI CRM Workflow Engine)\n"
            yield "- Thinking patterns and mindset\n"
            yield "- Technical skills and agentic AI experience"
            return

        # Filter to high-quality chunks only; always keep at least one
        context_items = [
            doc for doc, dist in general_results if dist < 1.0
        ]
        if not context_items:
            context_items = [general_results[0][0]]

        context = "\n\n---\n\n".join(context_items)
        async for token in self._stream_general_response(
            user_message, context
        ):
            yield token

    # ------------------------------------------------------------------ #
    # FAQ response — answer is pre-written, LLM formats it lightly
    # ------------------------------------------------------------------ #

    async def _stream_faq_response(
        self, user_message: str, faq_doc: str
    ) -> AsyncGenerator[str, None]:

        system_prompt = """You are presenting Vinayaka Hegde's portfolio to a cofounder.
The ANSWER BLOCK below is the authoritative, pre-written answer for this question.
Your ONLY job is to output it exactly as written — preserving every ## heading, every - bullet, and every **bold** marker.
Do NOT add intros, summaries, disclaimers, or extra sentences.
Do NOT reorder or merge bullets.
Output the answer block and nothing else."""

        user_content = f"""Question: {user_message}

ANSWER BLOCK:
{_extract_answer_block(faq_doc)}"""

        async for token in self.llm.stream_response(
            system_prompt, user_content, context=""
        ):
            yield token

    # ------------------------------------------------------------------ #
    # General response — LLM synthesises from retrieved chunks
    # ------------------------------------------------------------------ #

    async def _stream_general_response(
        self, user_message: str, context: str
    ) -> AsyncGenerator[str, None]:

        system_prompt = """You are presenting Vinayaka Hegde's portfolio to a potential cofounder. Answer with the confidence and directness of a YC founder — no hedging, no filler.

RULES:
1. Answer ONLY what is asked. Do not pad with unrelated context.
2. Lead with the most impressive, specific fact. Never open with "Vin believes" or "Vin thinks".
3. Use EXACT names, metrics, and technologies from the context: IncidentCopilot, LangGraph, AWS Bedrock, Titan Embed v2, BM25, Amazon Rerank v1, ~50% MTTR, 30% precision, 40% hallucination reduction, FastAPI CRM, 60K+ records, 35% latency reduction.
4. Maximum 3 bullets. Each bullet must be one tight, specific sentence.
5. Format:
   ## [Short Heading]
   One-sentence direct answer.

   - **[Label]**: specific detail with exact metric or technology
   - **[Label]**: specific detail with exact metric or technology
   - **[Label]**: specific detail with exact metric or technology

6. Bold: project names, metric numbers, technology names.
7. If the context does not contain the answer, say: "I don't have that detail in Vinayaka's portfolio."
8. Never invent metrics or achievements.

Priority: IncidentCopilot first. FastAPI CRM second. Everything else only if directly relevant."""

        async for token in self.llm.stream_response(
            system_prompt, user_message, context
        ):
            yield token


# ------------------------------------------------------------------ #
# Helper: extract just the answer portion of a FAQ chunk
# ------------------------------------------------------------------ #

def _extract_answer_block(faq_chunk: str) -> str:
    """
    A FAQ chunk looks like:

        ## Q: Question text | variant | variant

        ## Answer Heading
        - bullet ...

    We want everything AFTER the '## Q:' line.
    """
    lines = faq_chunk.splitlines()
    answer_lines = []
    past_q_line = False
    for line in lines:
        if not past_q_line:
            if line.startswith("## Q:"):
                past_q_line = True
            continue
        answer_lines.append(line)

    # Strip leading blank lines
    while answer_lines and not answer_lines[0].strip():
        answer_lines.pop(0)

    return "\n".join(answer_lines).strip()
