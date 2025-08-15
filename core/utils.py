import uuid
from typing import List
from langchain_core.messages import BaseMessage, SystemMessage


def new_session_id() -> str:
    return str(uuid.uuid4())


def build_runtime_messages(system_prompt: str, history_messages: List[BaseMessage]) -> List[BaseMessage]:
    return [SystemMessage(content=system_prompt)] + list(history_messages)