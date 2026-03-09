from langchain_core.chat_history import InMemoryChatMessageHistory

class MemoryManager:
    def __init__(self, k=10):
        self.k = k
        self.sessions: dict[str, InMemoryChatMessageHistory] = {}

    def _get_or_create(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()
        return self.sessions[session_id]

    def add_user_message(self, session_id: str, message: str):
        self._get_or_create(session_id).add_user_message(message)

    def add_ai_message(self, session_id: str, message: str):
        self._get_or_create(session_id).add_ai_message(message)

    def get_context(self, session_id: str) -> list:
        history = self._get_or_create(session_id)
        # Return last k*2 messages (user+ai pairs)
        return history.messages[-(self.k * 2):]
