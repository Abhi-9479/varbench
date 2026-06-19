"""Categorical grader: actual must be one of allowed_labels and equal to expected."""
from __future__ import annotations

from typing import Any

from varbench.graders.base import Grader, GraderResult


class CategoricalGrader(Grader):
    """For ACMG classes, refusal labels, etc."""

    def grade(self, expected: Any, actual: Any) -> GraderResult:
        if actual is None:
            return self._wrap(False, expected, actual, "no answer produced")

        e, a = str(expected), str(actual)
        if not self.config.case_sensitive:
            e, a = e.lower(), a.lower()

        allowed = self.config.allowed_labels or []
        allowed_norm = [s if self.config.case_sensitive else s.lower() for s in allowed]
        if allowed_norm and a not in allowed_norm:
            return self._wrap(False, expected, actual,
                              f"actual={actual!r} is not in allowed_labels={allowed}")

        passed = e == a
        reason = "label matches" if passed else f"expected {expected!r}, got {actual!r}"
        return self._wrap(passed, expected, actual, reason)
