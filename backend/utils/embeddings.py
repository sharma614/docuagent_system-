from sentence_transformers import SentenceTransformer
import os

class EmbeddingProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingProvider, cls).__new__(cls)
            # Lightweight model: 384 dims, ~90MB, fast on CPU
            # Must match the Pinecone index dimension (384)
            print("[Embeddings] Loading sentence-transformer model...")
            cls._instance.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[Embeddings] Model loaded.")
        return cls._instance

    def embed_query(self, text: str) -> list:
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_documents(self, texts: list) -> list:
        return self.model.encode(texts, convert_to_numpy=True).tolist()
