import os
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv

load_dotenv()

class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229", # Using sonnet 3 as requested (or 3.5 if available, prompt says sonnet)
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        
        # Define the specialized agents and their roles
        self.response_schemas = [
            ResponseSchema(name="agent", description="The name of the agent to delegate to: 'retrieval', 'qa', 'summarizer', 'translator', 'data_extraction', 'email_drafting'"),
            ResponseSchema(name="reasoning", description="Brief explanation of why this agent was chosen"),
            ResponseSchema(name="parameters", description="JSON object containing parameters for the chosen agent (e.g., target_language for translator, doc_id for summarizer)")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        
        self.prompt = ChatPromptTemplate.from_template(
            "You are the Orchestrator for the DocuAgent System. Your goal is to route the user's request to the correct specialized agent.\n"
            "Available Agents:\n"
            "- retrieval: For searching information across documents.\n"
            "- qa: For answering specific questions based on document content.\n"
            "- summarizer: For summarizing one or more documents.\n"
            "- translator: For translating content to another language.\n"
            "- data_extraction: For extracting structured data like tables or entities.\n"
            "- email_drafting: For drafting professional emails based on document content.\n\n"
            "User Request: {user_input}\n\n"
            "{format_instructions}\n"
            "Reasoning logs are critical for transparency."
        )

    def route(self, user_input: str):
        format_instructions = self.output_parser.get_format_instructions()
        _input = self.prompt.format_prompt(user_input=user_input, format_instructions=format_instructions)
        output = self.llm.predict(_input.to_string())
        return self.output_parser.parse(output)
