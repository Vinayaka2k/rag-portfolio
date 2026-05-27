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
    """Chunk text with sliding window, preserving section headers"""
    chunks = []
    
    # Split by major sections first
    sections = text.split("## ")
    
    for section in sections:
        if not section.strip():
            continue
        
        # Add section header back
        section_text = f"## {section}" if not section.startswith("##") else section
        
        # Chunk within each section
        start = 0
        while start < len(section_text):
            end = min(start + chunk_size, len(section_text))
            chunk = section_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
    
    return chunks
