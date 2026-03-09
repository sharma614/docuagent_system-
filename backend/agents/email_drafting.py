import os
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class EmailDraftingAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7 # Slightly higher temperature for drafting
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Based on the following document context and the user's intent, draft a professional email.\n\n"
            "Context:\n{context}\n\n"
            "Intent/Requirement: {intent}\n\n"
            "Email Draft (Subject and Body):"
        )

    def draft(self, context_chunks: list, intent: str):
        context_text = "\n\n".join([c['text'] for c in context_chunks[:10]])
        _input = self.prompt.format_prompt(context=context_text, intent=intent)
        response = self.llm.predict(_input.to_string())
        return response
