import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import json
import re

load_dotenv()

class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "You are the Orchestrator for the DocuAgent System. Route the user's request to the correct agent.\n"
            "Available Agents:\n"
            "- retrieval: Search for information across documents.\n"
            "- qa: Answer specific questions based on document content.\n"
            "- summarizer: Summarize one or more documents.\n"
            "- translator: Translate content to another language.\n"
            "- data_extraction: Extract structured data (tables, entities).\n"
            "- email_drafting: Draft professional emails using document context.\n\n"
            "User Request: {user_input}\n\n"
            'Respond ONLY with a raw JSON object (no markdown) like: {{"agent": "qa", "reasoning": "...", "parameters": {{}}}}'
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def route(self, user_input: str):
        output = self.chain.invoke({"user_input": user_input})
        try:
            # Strip markdown code fences if present
            output = re.sub(r"```json|```", "", output).strip()
            return json.loads(output)
        except Exception:
            return {"agent": "qa", "reasoning": "Fallback to QA agent.", "parameters": {}}
