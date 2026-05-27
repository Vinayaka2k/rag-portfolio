"""FastAPI RAG Portfolio Backend"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CHROMADB_PATH = "./data/chromadb"
DATA_DIR = "./data"
MODEL_NAME = "all-MiniLM-L6-v2"
