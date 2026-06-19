"""Debug agents that don't call any LLM."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EchoAgent:
    """Writes the expected answer verbatim. Always passes a correct eval.

    Useful as a smoke test: if EchoAgent fails an eval, the grader or runner
    has a bug, not the agent.
    """

    def __init__(self, answer_key: str, expected_answer: Any) -> None:
        self.answer_key = answer_key
        self.expected_answer = expected_answer

    def __call__(self, task_prompt: str, work_dir: Path) -> None:
        out = {self.answer_key: self.expected_answer}
        (work_dir / "eval_answer.json").write_text(json.dumps(out, indent=2))


class NullAgent:
    """Writes an empty JSON. Always fails (the key is missing)."""

    def __call__(self, task_prompt: str, work_dir: Path) -> None:
        (work_dir / "eval_answer.json").write_text("{}")
