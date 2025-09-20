import os
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

def _cosine(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_gemini_embedding(text: str) -> np.ndarray:
    """Returns the embedding for a given text using the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    genai.configure(api_key=api_key)
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(result['embedding'], dtype=float)

def get_fallback_embedding(text: str) -> np.ndarray:
    """Returns the embedding for a given text using Sentence-Transformers as a fallback."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode(text, show_progress_bar=False)
    return np.array(emb, dtype=float)

def similarity_between_texts(a: str, b: str) -> float:
    try:
        ea = get_gemini_embedding(a)
        eb = get_gemini_embedding(b)
        return _cosine(ea, eb)
    except Exception as e:
        print(f"Gemini API failed, falling back to local model: {e}")
        ea = get_fallback_embedding(a)
        eb = get_fallback_embedding(b)
        return _cosine(ea, eb)