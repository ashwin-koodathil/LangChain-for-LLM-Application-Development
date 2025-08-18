import time
import streamlit as st

from settings import (
    DB_PATH,
    SQL_URL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_SEED,
    DEFAULT_SYSTEM_PROMPT,
    SUMMARY_LIMIT_CHARS,
    SUMMARY_KEEP_LAST,
)

from core.llm import build_llm
from core.history import get_history, clear_history, render_streamlit_history
from core.memory import maybe_summarize_memory
from core.logs import init_db, log_event, export_logs, fetch_recent_logs
from core.utils import new_session_id, build_runtime_messages

st.set_page_config(page_title="Llama3 Chat • Memory + Logging", page_icon="💬", layout="wide")

# ---------- Sidebar: Session & Model ----------
st.sidebar.header("⚙️ Settings")

if "session_id" not in st.session_state:
    st.session_state.session_id = "default"

session_id = st.sidebar.text_input("Session ID", value=st.session_state.session_id)
if st.sidebar.button("New Session (UUID)"):
    session_id = new_session_id()

if session_id != st.session_state.session_id:
    st.session_state.session_id = session_id

model_name = st.sidebar.selectbox("Model Name", ("llama3", "llama3-70b", "llama3-8b", "llama3-70b-instruct", "llama3-8b-instruct"), index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.5, DEFAULT_TEMPERATURE, 0.05)
top_p = st.sidebar.slider("Top-p", 0.0, 1.0, DEFAULT_TOP_P, 0.05)
seed = st.sidebar.number_input("Seed", value=DEFAULT_SEED, step=1)

system_prompt = st.sidebar.text_area("System Prompt", value=DEFAULT_SYSTEM_PROMPT, height=80)

# Logging & Memory options
enable_logging = st.sidebar.checkbox("Enable logging", value=True)
summarize_toggle = st.sidebar.checkbox("Auto-summarize long chats", value=True)
limit_chars = st.sidebar.slider("Summarize when characters exceed", 2_000, 50_000, SUMMARY_LIMIT_CHARS, 500)
keep_last = st.sidebar.slider("Keep last N messages verbatim", 2, 30, SUMMARY_KEEP_LAST, 1)

# Export / maintenance
col_a, col_b, col_c = st.sidebar.columns([1,1,1])
with col_a:
    export_btn = st.button("Export Logs")
with col_b:
    clear_chat_btn = st.button("Clear Chat")
with col_c:
    show_logs_btn = st.button("Show Logs")

# ---------- Init DB, LLM, History ----------
init_db(DB_PATH)
llm = build_llm(model=model_name, temperature=temperature, top_p=top_p, seed=seed)
history = get_history(st.session_state.session_id, SQL_URL)

# Maintenance actions
if clear_chat_btn:
    clear_history(history)
    log_event(DB_PATH, st.session_state.session_id, "chat_cleared", {}, enabled=enable_logging)
    st.experimental_rerun()

if export_btn:
    data = export_logs(DB_PATH, st.session_state.session_id)
    st.download_button("Download session logs (.jsonl)", data=data, file_name=f"logs_{st.session_state.session_id}.jsonl", mime="application/json")

if show_logs_btn:
    st.sidebar.markdown("#### Recent Logs (50)")
    for ts, event, payload in fetch_recent_logs(DB_PATH, st.session_state.session_id, limit=50):
        st.sidebar.code(f"{ts} | {event}\n{payload}")

# ---------- Main UI ----------
st.title("Ash-The Story Teller 💬")
st.caption("Streamlit • LangChain • Ollama • SQLite")

# Render prior messages
render_streamlit_history(st, history)

# Chat input
user_input = st.chat_input("Type your message…")

if user_input:
    # Persist user message
    history.add_user_message(user_input)
    log_event(DB_PATH, st.session_state.session_id, "user_message", {
        "text": user_input,
        "model": model_name,
        "temperature": temperature,
        "top_p": top_p,
        "seed": seed,
    }, enabled=enable_logging)

    runtime_messages = build_runtime_messages(system_prompt, history.messages)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        t0 = time.time()
        try:
            for chunk in llm.stream(runtime_messages):
                full_text += chunk.content or ""
                placeholder.markdown(full_text)
        except Exception as e:
            log_event(DB_PATH, st.session_state.session_id, "llm_error", {"error": str(e)}, enabled=enable_logging)
            st.error(f"LLM error: {e}")
        dt = time.time() - t0

    if full_text:
        history.add_ai_message(full_text)
        log_event(DB_PATH, st.session_state.session_id, "assistant_message", {
            "chars": len(full_text),
            "latency_sec": round(dt, 3),
        }, enabled=enable_logging)

    if summarize_toggle:
        maybe_summarize_memory(
            history=history,
            llm=llm,
            limit_chars=limit_chars,
            keep_last=keep_last,
            st=st,
            log_func=lambda sid, ev, payload: log_event(DB_PATH, sid, ev, payload, enabled=enable_logging),
            session_id=st.session_state.session_id,
        )

# Footer
st.markdown(
    """
    ---
    **Tips**
    - Switch *Session ID*s to keep separate histories (persisted in `chat.db`).
    - Toggle **Enable logging** to record events in `logs` table.
    - Adjust **System Prompt** any time; it's applied at runtime.
    - **Auto-summarize** keeps context compact on long chats.
    """
)