"""Built-in agents."""
from __future__ import annotations

from varbench.agents.debug import EchoAgent, NullAgent

__all__ = ["EchoAgent", "NullAgent", "get_agent"]


def get_agent(name: str, model: str | None = None,
              expected_answer=None, answer_key: str = "answer",
              verbose: bool = False):
    """Return an agent function by name.

    Debug agents: echo, null (no model needed).
    LLM agents: claude (Anthropic API), ollama (local).
    """
    name = name.lower()

    if name == "echo":
        if expected_answer is None:
            raise ValueError("echo agent needs expected_answer (CLI passes it in)")
        return EchoAgent(answer_key=answer_key, expected_answer=expected_answer)

    if name == "null":
        return NullAgent()

    if name == "claude":
        from varbench.agents.claude import ClaudeAgent, DEFAULT_MODEL
        return ClaudeAgent(model=model or DEFAULT_MODEL, verbose=verbose)

    if name == "ollama":
        from varbench.agents.ollama_agent import OllamaAgent, DEFAULT_MODEL
        return OllamaAgent(model=model or DEFAULT_MODEL, verbose=verbose)

    raise ValueError(
        f"Unknown agent: {name!r}. Available: echo, null, claude, ollama."
    )
