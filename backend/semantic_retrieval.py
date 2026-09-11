import re
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

# Try loading sentence-transformers, fallback to TF-IDF vectorizer if offline
_SENTENCE_TRANSFORMER_MODEL = None

def get_embedding_model():
    global _SENTENCE_TRANSFORMER_MODEL
    if _SENTENCE_TRANSFORMER_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Load lightweight local model
            _SENTENCE_TRANSFORMER_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
            print("[+] Initialized local SentenceTransformer vector model: all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[-] Could not load SentenceTransformer ({e}). Using TF-IDF vector embeddings fallback.")
            _SENTENCE_TRANSFORMER_MODEL = False
    return _SENTENCE_TRANSFORMER_MODEL

def compute_semantic_vector_similarity(query: str, corpus: List[str]) -> List[float]:
    """
    Compute dense semantic vector embeddings using SentenceTransformer (or dense TF-IDF fallback)
    and return cosine similarity scores.
    """
    if not corpus:
        return []

    model = get_embedding_model()

    if model:
        try:
            query_embedding = model.encode([query], convert_to_tensor=False)[0]
            corpus_embeddings = model.encode(corpus, convert_to_tensor=False)
            
            # Cosine similarity
            q_norm = np.linalg.norm(query_embedding)
            sims = []
            for doc_emb in corpus_embeddings:
                d_norm = np.linalg.norm(doc_emb)
                if q_norm > 0 and d_norm > 0:
                    sim = float(np.dot(query_embedding, doc_emb) / (q_norm * d_norm))
                else:
                    sim = 0.0
                sims.append(max(0.0, min(1.0, sim)))
            return sims
        except Exception as e:
            print(f"[-] Vector similarity computation error: {e}")

    # Fallback to TfidfVectorizer Cosine Similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([query] + corpus)
        sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        return [float(max(0.0, min(1.0, s))) for s in sims]
    except Exception:
        return [0.5] * len(corpus)
