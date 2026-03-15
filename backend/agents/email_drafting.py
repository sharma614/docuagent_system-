import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class EmailDraftingAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Based on the following document context and user's intent, draft a professional email.\n\n"
            "Context:\n{context}\n\n"
            "Intent/Requirement: {intent}\n\n"
            "Email Draft (Subject and Body):"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def draft(self, context_chunks: list, intent: str):
        context_text = "\n\n".join([c['text'] for c in context_chunks[:10]])
        return self.chain.invoke({"context": context_text, "intent": intent})
