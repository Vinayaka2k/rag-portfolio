"""Test for response truncation issue"""
import asyncio
from data_loader import load_data, chunk_text
from rag_chain import RAGChain

async def test():
    # Load data
    portfolio_data = load_data()
    chunks = chunk_text(portfolio_data, chunk_size=600, overlap=50)
    
    # Setup RAG
    rag = RAGChain()
    rag.setup(chunks)
    
    # Test query
    query = 'What is the most impressive thing built by Vin?'
    print(f'Query: {query}\n')
    print('|START|')
    
    full_response = ""
    async for token in rag.query(query):
        full_response += token
        print(token, end='', flush=True)
    
    print('|END|\n')
    print(f'\nFull response length: {len(full_response)} chars')
    print(f'First 100 chars: {repr(full_response[:100])}')
    print(f'Last 100 chars: {repr(full_response[-100:])}')

asyncio.run(test())
