import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class SummarizerAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Summarize the following document content. Provide a concise summary followed by key bullet points.\n\n"
            "Content:\n{content}\n\n"
            "Summary:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def summarize(self, content_chunks: list):
        full_text = "\n\n".join([c['text'] for c in content_chunks[:10]])
        return self.chain.invoke({"content": full_text})
