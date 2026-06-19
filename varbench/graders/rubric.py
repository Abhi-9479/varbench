"""LLM-judge grader: scores free-text answers against a rubric.

Stubbed for now — calls an LLM only if config.judge_model is set.
Real implementation lands in Day 4 once we wire up the Claude client.
"""
from __future__ import annotations

from typing import Any

from varbench.graders.base import Grader, GraderResult


class RubricGrader(Grader):
    def grade(self, expected: Any, actual: Any) -> GraderResult:
        return self._wrap(
            False, expected, actual,
            "RubricGrader is not yet implemented (Day 4). "
            "Use exact/numeric/set_match/categorical for canonical evals.",
        )
