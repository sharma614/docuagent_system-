import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class DataExtractionAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Extract structured data from the following document content. "
            "Identify tables, key-value pairs, and entities (people, organizations, dates). "
            "Return the result STRICTLY as a raw JSON object (no markdown) with keys: 'tables', 'kv_pairs', 'entities'.\n\n"
            "Content:\n{content}\n\n"
            "JSON Output:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def extract(self, content_chunks: list):
        full_text = "\n\n".join([c['text'] for c in content_chunks[:5]])
        response = self.chain.invoke({"content": full_text})
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            return json.loads(response[json_start:json_end])
        except Exception:
            return {"error": "Failed to extract structured data", "raw": response}
