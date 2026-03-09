import os
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class SummarizerAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "Summarize the following document content. Provide a concise summary followed by key bullet points.\n\n"
            "Content:\n{content}\n\n"
            "Summary:"
        )

    def summarize(self, content_chunks: list):
        # Concatenate chunks for summarization (handle token limits if needed)
        full_text = "\n\n".join([c['text'] for c in content_chunks[:10]]) # Limit to first 10 chunks for now
        _input = self.prompt.format_prompt(content=full_text)
        response = self.llm.predict(_input.to_string())
        return response
