"""Base class and result type for all graders."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from varbench.eval_spec import GraderConfig


@dataclass
class GraderResult:
    """The output of grading a single answer."""
    passed: bool
    score: float           # 0.0 to 1.0; for binary graders, 0.0 or 1.0
    reason: str            # human-readable explanation
    expected: Any
    actual: Any


class Grader(ABC):
    """Abstract base class. Subclasses implement `grade`."""

    def __init__(self, config: GraderConfig) -> None:
        self.config = config

    @abstractmethod
    def grade(self, expected: Any, actual: Any) -> GraderResult:
        ...

    def _wrap(self, passed: bool, expected: Any, actual: Any, reason: str,
              score: float | None = None) -> GraderResult:
        """Helper to build a GraderResult with sensible defaults."""
        if score is None:
            score = 1.0 if passed else 0.0
        return GraderResult(passed=passed, score=score, reason=reason,
                            expected=expected, actual=actual)
