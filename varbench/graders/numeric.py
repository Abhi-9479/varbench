"""Numeric grader: float comparison with absolute and/or relative tolerance."""
from __future__ import annotations

import math
from typing import Any

from varbench.graders.base import Grader, GraderResult


class NumericGrader(Grader):
    """Pass if |actual - expected| <= tolerance OR within rel_tolerance."""

    def grade(self, expected: Any, actual: Any) -> GraderResult:
        if actual is None:
            return self._wrap(False, expected, actual, "no answer produced")

        try:
            e = float(expected)
            a = float(actual)
        except (TypeError, ValueError):
            return self._wrap(False, expected, actual,
                              f"could not coerce to float: expected={expected!r}, actual={actual!r}")

        if math.isnan(a):
            return self._wrap(False, expected, actual, "actual is NaN")

        abs_tol = self.config.tolerance if self.config.tolerance is not None else 0.0
        rel_tol = self.config.rel_tolerance if self.config.rel_tolerance is not None else 0.0
        diff = abs(a - e)
        passed = diff <= abs_tol or (e != 0 and diff / abs(e) <= rel_tol)

        reason = (f"|{a} - {e}| = {diff:.6g}; abs_tol={abs_tol}, rel_tol={rel_tol} -> "
                  f"{'pass' if passed else 'fail'}")
        return self._wrap(passed, expected, actual, reason)
