import os
import uuid
from PyPDF2 import PdfReader
import docx2txt
try:
    from backend.utils.pinecone_client import PineconeClient
    from backend.utils.embeddings import EmbeddingProvider
except ImportError:
    from utils.pinecone_client import PineconeClient
    from utils.embeddings import EmbeddingProvider
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

class IngestionAgent:
    def __init__(self):
        self.pc_client = PineconeClient()
        self.embed_provider = EmbeddingProvider()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

    def process_file(self, file_path: str, doc_name: str):
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()
        elif ext == ".docx":
            text = docx2txt.process(file_path)
        else: # .txt
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        doc_id = str(uuid.uuid4())
        chunks = self.text_splitter.split_text(text)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self.embed_provider.embed_query(chunk)
            vectors.append({
                "id": f"{doc_id}_{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "doc_name": doc_name,
                    "doc_id": doc_id,
                    "chunk_index": i
                }
            })

        # Upsert to Pinecone in the document-specific namespace (or general if preferred, using per-doc for isolation as requested)
        self.pc_client.upsert_vectors(vectors, namespace=doc_id)
        
        return {
            "doc_id": doc_id,
            "doc_name": doc_name,
            "status": "success",
            "chunks_processed": len(chunks)
        }
