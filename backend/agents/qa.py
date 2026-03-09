import os
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class QAAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant. Answer the user's question based ONLY on the provided context.\n"
            "If the answer is not in the context, say that you don't know.\n"
            "Always cite your sources by mentioning the document name.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

    def answer(self, question: str, context_chunks: list):
        context_text = "\n\n".join([f"Source: {c['doc_name']}\nContent: {c['text']}" for c in context_chunks])
        _input = self.prompt.format_prompt(context=context_text, question=question)
        response = self.llm.predict(_input.to_string())
        return response
