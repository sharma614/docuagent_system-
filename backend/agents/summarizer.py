import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class SummarizerAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
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
