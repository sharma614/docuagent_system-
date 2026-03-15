try:
    from backend.utils.pinecone_client import PineconeClient
    from backend.utils.embeddings import EmbeddingProvider
except ImportError:
    from utils.pinecone_client import PineconeClient
    from utils.embeddings import EmbeddingProvider

class RetrievalAgent:
    def __init__(self):
        self.pc_client = PineconeClient()
        self.embed_provider = EmbeddingProvider()

    def search(self, query: str, namespace: str = None, top_k: int = 5):
        query_vector = self.embed_provider.embed_query(query)
        results = self.pc_client.query_vectors(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace
        )
        
        matches = []
        for match in results.get('matches', []):
            matches.append({
                "text": match['metadata']['text'],
                "doc_name": match['metadata']['doc_name'],
                "doc_id": match['metadata']['doc_id'],
                "score": match['score']
            })
            
        return matches
