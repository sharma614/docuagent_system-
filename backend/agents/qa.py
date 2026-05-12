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
            "You are a helpful assistant. Answer the user's question based ONLY on the provided document context.\n"
            "If the answer is not in the context, say you don't know.\n"
            "Always cite sources by mentioning the document name.\n\n"
            "{history}"
            "Document Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def answer(self, question: str, context_chunks: list, history: list = None) -> str:
        context_text = "\n\n".join(
            [f"Source: {c['doc_name']}\nContent: {c['text']}" for c in context_chunks]
        )
        history_block = _format_history(history)
        return self.chain.invoke({
            "context": context_text,
            "question": question,
            "history": history_block,
        })


def _format_history(history: list | None) -> str:
    """Format last 5 conversation turns into a readable block."""
    if not history:
        return ""
    lines = []
    for msg in history[-(10):]:
        role = "User" if msg.type == "human" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "Previous conversation:\n" + "\n".join(lines) + "\n\n" if lines else ""
