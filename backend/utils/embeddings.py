from langchain_community.embeddings import HuggingFaceEmbeddings
import os

class EmbeddingProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingProvider, cls).__new__(cls)
            # Using BGE Large (1024 dimensions) to match your Pinecone index
            cls._instance.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-large-en-v1.5"
            )
        return cls._instance

    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]):
        return self.embeddings.embed_documents(texts)
