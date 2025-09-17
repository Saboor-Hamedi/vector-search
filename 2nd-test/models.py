from sentence_transformers import SentenceTransformer


def ai_model(text="all-MiniLM-L6-v2"):
    return SentenceTransformer(text)
