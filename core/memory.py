from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


def char_len(messages: List[BaseMessage]) -> int:
    return sum(len(getattr(m, "content", "") or "") for m in messages)


def maybe_summarize_memory(history, llm, limit_chars: int, keep_last: int, st=None, log_func=None, session_id: str = "") -> bool:
    """Summarize older turns into a compact memory if total characters exceed limit.
    Keeps the last `keep_last` messages verbatim. Returns True if summarization happened.
    """
    msgs: List[BaseMessage] = history.messages
    if char_len(msgs) <= limit_chars:
        return False

    transcript_lines: List[str] = []
    for m in msgs:
        if isinstance(m, HumanMessage):
            transcript_lines.append(f"User: {m.content}")
        elif isinstance(m, AIMessage):
            transcript_lines.append(f"Assistant: {m.content}")
    long_text = "\n".join(transcript_lines)

    prompt = (
        "You are compressing a long chat into a concise memory for future turns.\n"
        "Extract key facts, user preferences, constraints, names, and unresolved questions.\n"
        "Return 8-14 bullet points. Be specific; keep numbers, URLs, and decisions.\n\n"
        f"Conversation:\n{long_text}"
    )

    try:
        summary = llm.invoke(prompt).content
    except Exception as e:
        if log_func:
            log_func(session_id, "memory_summary_error", {"error": str(e)})
        return False

    tail = msgs[-keep_last:] if keep_last > 0 else []
    pre_chars = char_len(msgs)

    # Rewrite history: insert memory summary as the first AI message, then append tail
    history.clear()
    history.add_ai_message("[MEMORY SUMMARY]\n" + (summary or ""))
    for m in tail:
        if isinstance(m, HumanMessage):
            history.add_user_message(m.content)
        elif isinstance(m, AIMessage):
            history.add_ai_message(m.content)

    post_chars = char_len(history.messages)

    if log_func:
        log_func(session_id, "memory_summarized", {
            "pre_chars": pre_chars,
            "post_chars": post_chars,
            "kept_messages": len(tail),
            "summary_chars": len(summary or ""),
        })

    if st:
        st.info("Conversation long — older turns summarized into a compact memory note.")
    return True
