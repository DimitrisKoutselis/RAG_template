from enum import Enum


class MessageRole(Enum):
    """Enumeration of possible message roles in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
