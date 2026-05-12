import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


def _format_history(history: list | None) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-(10):]:
        role = "User" if msg.type == "human" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "Previous conversation:\n" + "\n".join(lines) + "\n\n" if lines else ""


class SummarizerAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Summarize the following document content. Provide a concise summary followed by key bullet points.\n\n"
            "{history}"
            "Content:\n{content}\n\n"
            "Summary:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def summarize(self, content_chunks: list, history: list = None) -> str:
        full_text = "\n\n".join([c["text"] for c in content_chunks[:10]])
        return self.chain.invoke({
            "content": full_text,
            "history": _format_history(history),
        })
