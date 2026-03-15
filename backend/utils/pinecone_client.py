from pinecone import Pinecone, ServerlessSpec
import os
import time
from dotenv import load_dotenv

load_dotenv()

class PineconeClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PineconeClient, cls).__new__(cls)
            api_key = os.getenv("PINECONE_API_KEY")
            cls._instance._pc = Pinecone(api_key=api_key)
            cls._instance.index_name = os.getenv("PINECONE_INDEX_NAME", "docuagent")

            # Check if index exists — if not, create it
            existing = [idx.name for idx in cls._instance._pc.list_indexes()]
            if cls._instance.index_name not in existing:
                print(f"[Pinecone] Index '{cls._instance.index_name}' not found. Creating...")
                cls._instance._pc.create_index(
                    name=cls._instance.index_name,
                    dimension=384,   # matches all-MiniLM-L6-v2
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                # Wait until ready (up to 60s)
                for _ in range(30):
                    try:
                        info = cls._instance._pc.describe_index(cls._instance.index_name)
                        if info.status.get("ready", False):
                            break
                    except Exception:
                        pass
                    print("[Pinecone] Waiting for index to be ready...")
                    time.sleep(2)
                print(f"[Pinecone] Index '{cls._instance.index_name}' is ready.")
            else:
                print(f"[Pinecone] Using existing index '{cls._instance.index_name}'.")

            cls._instance.index = cls._instance._pc.Index(cls._instance.index_name)
        return cls._instance

    def upsert_vectors(self, vectors, namespace):
        return self.index.upsert(vectors=vectors, namespace=namespace)

    def query_vectors(self, vector, top_k=5, namespace=None, filter=None):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=True
        )

    def delete_vectors(self, ids, namespace):
        return self.index.delete(ids=ids, namespace=namespace)

    def list_namespaces(self):
        stats = self.index.describe_index_stats()
        return list(stats.get('namespaces', {}).keys())
