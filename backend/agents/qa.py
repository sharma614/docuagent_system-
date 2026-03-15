import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class QAAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant. Answer the user's question based ONLY on the provided context.\n"
            "If the answer is not in the context, say you don't know.\n"
            "Always cite sources by mentioning the document name.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def answer(self, question: str, context_chunks: list):
        context_text = "\n\n".join([f"Source: {c['doc_name']}\nContent: {c['text']}" for c in context_chunks])
        return self.chain.invoke({"context": context_text, "question": question})
