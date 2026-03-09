from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

class PineconeClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PineconeClient, cls).__new__(cls)
            cls._instance._pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            cls._instance.index_name = os.getenv("PINECONE_INDEX_NAME")
            cls._instance.index = cls._instance._pc.Index(cls._instance.index_name)
        return cls._instance

    def upsert_vectors(self, vectors, namespace):
        """
        vectors: list of dictionaries {'id': str, 'values': list, 'metadata': dict}
        """
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
        # Note: This might require specific Pinecone versions or API calls
        stats = self.index.describe_index_stats()
        return stats.get('namespaces', {}).keys()
