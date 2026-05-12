import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


class ComparisonAgent:
    """Compares content from two different documents side-by-side."""

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "You are a document comparison expert. Analyze the content from two documents and provide a detailed comparison.\n\n"
            "Document A — {doc_a_name}:\n{context_a}\n\n"
            "Document B — {doc_b_name}:\n{context_b}\n\n"
            "User's comparison focus: {query}\n\n"
            "Provide a structured comparison with these sections:\n"
            "1. **Key Similarities** — what both documents share\n"
            "2. **Key Differences** — what sets them apart\n"
            "3. **Document A Strengths** — what A covers that B doesn't\n"
            "4. **Document B Strengths** — what B covers that A doesn't\n"
            "5. **Recommendation** — which document is more relevant to the user's query and why\n\n"
            "Be specific and cite content from both documents."
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def compare(
        self,
        chunks_a: list,
        chunks_b: list,
        query: str,
        doc_a_name: str = "Document A",
        doc_b_name: str = "Document B",
        history: list = None,
    ) -> str:
        context_a = "\n\n".join([c["text"] for c in chunks_a[:8]])
        context_b = "\n\n".join([c["text"] for c in chunks_b[:8]])

        history_block = ""
        if history:
            pairs = []
            for msg in history[-(6):]:
                role = "User" if msg.type == "human" else "Assistant"
                pairs.append(f"{role}: {msg.content}")
            if pairs:
                history_block = "Previous conversation:\n" + "\n".join(pairs) + "\n\n"

        return self.chain.invoke({
            "doc_a_name": doc_a_name,
            "doc_b_name": doc_b_name,
            "context_a": history_block + context_a,
            "context_b": context_b,
            "query": query,
        })
