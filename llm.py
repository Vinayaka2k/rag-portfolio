"""LLM integration with Groq"""
import aiohttp
from typing import AsyncGenerator
from config import GROQ_API_KEY

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class GroqLLM:
    def __init__(self, api_key: str = GROQ_API_KEY, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model  # Latest Llama 3.3 70B model
    
    async def stream_response(
        self,
        system_prompt: str,
        user_message: str,
        context: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream response from Groq API with optimized parameters"""
        
        # Format the context clearly for the LLM
        if context:
            context_section = f"""**CONTEXT FROM PORTFOLIO:**

{context}

---"""
        else:
            context_section = ""
        
        # Build the user message with clear structure
        full_message = f"""{context_section}

**QUESTION:** {user_message}

Please provide a direct, insightful answer grounded in the context above."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_message}
            ],
            "temperature": 0.6,  # Reduced from 0.7 for more grounded responses
            "top_p": 0.9,  # Focus on higher probability tokens
            "max_tokens": 1500,  # Increased from 1024 for more detailed responses
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(GROQ_API_URL, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        yield f"Error: {resp.status} - {error_text}"
                        return
                    
                    async for line in resp.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                if 'choices' in chunk:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except:
                                pass
        except Exception as e:
            yield f"Error: {str(e)}"

