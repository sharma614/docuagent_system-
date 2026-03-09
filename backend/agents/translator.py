import os
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class TranslatorAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Translate the following text to {target_language}. Detect the source language automatically.\n\n"
            "Text:\n{text}\n\n"
            "Translation:"
        )

    def translate(self, text: str, target_language: str):
        _input = self.prompt.format_prompt(text=text, target_language=target_language)
        response = self.llm.predict(_input.to_string())
        return response
