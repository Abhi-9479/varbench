"""Exact-match grader: string, int, or bool equality."""
from __future__ import annotations

from typing import Any

from varbench.graders.base import Grader, GraderResult


class ExactGrader(Grader):
    """Compare with == (optionally case-insensitive for strings)."""

    def grade(self, expected: Any, actual: Any) -> GraderResult:
        if actual is None:
            return self._wrap(False, expected, actual,
                              "Agent did not produce an answer for this key")

        e, a = expected, actual
        if isinstance(expected, str) and isinstance(actual, str) and not self.config.case_sensitive:
            e, a = expected.lower(), actual.lower()

        passed = e == a
        reason = "exact match" if passed else f"expected {expected!r}, got {actual!r}"
        return self._wrap(passed, expected, actual, reason)
