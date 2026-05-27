"""Data loading and chunking utilities"""
import os
from pathlib import Path
from typing import List

def load_data() -> str:
    """Load all data files and combine into one context"""
    data_dir = Path("./data")
    combined_text = ""
    
    # Load resume
    resume_path = data_dir / "resume.txt"
    if resume_path.exists():
        combined_text += f"## RESUME\n\n{resume_path.read_text()}\n\n"
    
    # Load mindset
    mindset_path = data_dir / "mindset.md"
    if mindset_path.exists():
        combined_text += f"## MINDSET & VALUES\n\n{mindset_path.read_text()}\n\n"
    
    # Load projects
    projects_path = data_dir / "projects.json"
    if projects_path.exists():
        combined_text += f"## NOTABLE PROJECTS\n\n{projects_path.read_text()}\n\n"
    
    return combined_text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Chunk text with sliding window"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    
    return [c for c in chunks if c]  # Filter empty chunks
