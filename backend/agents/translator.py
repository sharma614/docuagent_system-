import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class TranslatorAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Translate the following text to {target_language}. Detect the source language automatically.\n\n"
            "Text:\n{text}\n\n"
            "Translation:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def translate(self, text: str, target_language: str):
        return self.chain.invoke({"text": text, "target_language": target_language})
