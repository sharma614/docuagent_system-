import os
import json
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class DataExtractionAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Extract structured data from the following document content. "
            "Identify tables, key-value pairs, and entities (people, organizations, dates). "
            "Return the result STRICTLY as a JSON object with keys: 'tables', 'kv_pairs', 'entities'.\n\n"
            "Content:\n{content}\n\n"
            "JSON Output:"
        )

    def extract(self, content_chunks: list):
        full_text = "\n\n".join([c['text'] for c in content_chunks[:5]]) # Smaller subset for extraction
        _input = self.prompt.format_prompt(content=full_text)
        response = self.llm.predict(_input.to_string())
        try:
            # Clean up response to ensure valid JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            return json.loads(response[json_start:json_end])
        except Exception:
            return {"error": "Failed to extract structured data", "raw": response}
