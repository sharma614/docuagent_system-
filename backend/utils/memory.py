from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory

class MemoryManager:
    def __init__(self, k=10):
        self.k = k
        self.sessions = {}

    def get_memory(self, session_id: str):
        if session_id not in self.sessions:
            history = ChatMessageHistory()
            self.sessions[session_id] = ConversationBufferWindowMemory(
                chat_memory=history,
                return_messages=True,
                memory_key="chat_history",
                k=self.k
            )
        return self.sessions[session_id]

    def add_user_message(self, session_id: str, message: str):
        memory = self.get_memory(session_id)
        memory.chat_memory.add_user_message(message)

    def add_ai_message(self, session_id: str, message: str):
        memory = self.get_memory(session_id)
        memory.chat_memory.add_ai_message(message)

    def get_context(self, session_id: str):
        memory = self.get_memory(session_id)
        return memory.load_memory_variables({})["chat_history"]
