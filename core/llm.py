from typing import Any

try:
    from langchain_ollama import ChatOllama  # modern split-out package
except ModuleNotFoundError:  # fallback to community package if needed
    from langchain_community.chat_models import ChatOllama  # type: ignore


def build_llm(model: str, temperature: float, top_p: float, seed: int) -> Any:
    """Factory that returns an Ollama-backed ChatOllama instance."""
    return ChatOllama(model=model, temperature=temperature, top_p=top_p, seed=seed)