from typing import List
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


def get_history(session_id: str, sql_url: str) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(session_id=session_id, connection_string=sql_url)


def clear_history(history: SQLChatMessageHistory) -> None:
    history.clear()


def render_streamlit_history(st, history: SQLChatMessageHistory) -> None:
    for m in history.messages:
        if isinstance(m, HumanMessage):
            with st.chat_message("user"):
                st.markdown(m.content)
        elif isinstance(m, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(m.content)