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

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 50) -> List[str]:
    """Chunk text intelligently, preserving semantic units like projects"""
    chunks = []
    
    # Split by major sections first (##)
    sections = text.split("## ")
    
    for section in sections:
        if not section.strip():
            continue
        
        # Add section header back
        section_text = f"## {section}" if not section.startswith("##") else section
        section_name = section_text.split("\n")[0]
        
        # Special handling for NOTABLE PROJECTS (JSON format)
        if "NOTABLE PROJECTS" in section_name:
            # For JSON, split by project name patterns and keep chunks together
            project_chunks = _smart_chunk_json(section_text)
            chunks.extend(project_chunks)
        else:
            # For resume and mindset, use sliding window
            _chunk_with_window(section_text, chunks, chunk_size, overlap)
    
    return chunks


def _chunk_with_window(text: str, chunks: List[str], chunk_size: int, overlap: int):
    """Apply sliding window chunking to text"""
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap


def _smart_chunk_json(text: str) -> List[str]:
    """Smart chunking for JSON projects - split by project boundaries"""
    chunks = []
    
    # Find all project names (looking for "name": "XYZ - " pattern)
    import json
    
    # Try to parse the JSON within the text
    try:
        # Find the JSON structure
        json_start = text.find('{')
        if json_start == -1:
            return [text]  # No JSON found, return as-is
        
        # Extract just the JSON part
        json_str = text[json_start:]
        json_data = json.loads(json_str)
        
        # Add header before JSON
        header = text[:json_start].strip()
        if header:
            chunks.append(header)
        
        # Process each project separately
        if 'projects' in json_data:
            for project in json_data['projects']:
                project_json = json.dumps({"project": project}, indent=2)
                # Prefix with header context
                project_chunk = f"## NOTABLE PROJECTS\n\n{project_json}"
                chunks.append(project_chunk)
        
        return chunks if chunks else [text]
    
    except (json.JSONDecodeError, ValueError):
        # If JSON parsing fails, fall back to simple window chunking
        chunks_list = []
        _chunk_with_window(text, chunks_list, 600, 50)
        return chunks_list
