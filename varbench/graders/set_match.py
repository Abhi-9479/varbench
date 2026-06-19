"""Set-match grader: exact set equality or Jaccard similarity."""
from __future__ import annotations

from typing import Any

from varbench.graders.base import Grader, GraderResult


class SetMatchGrader(Grader):
    """
    Pass if set(actual) == set(expected) when jaccard_threshold is None.
    Otherwise pass if Jaccard >= jaccard_threshold, with the Jaccard score as the result.
    """

    def grade(self, expected: Any, actual: Any) -> GraderResult:
        if not isinstance(expected, (list, set, tuple)):
            return self._wrap(False, expected, actual,
                              f"expected must be a list/set, got {type(expected).__name__}")
        if actual is None:
            return self._wrap(False, expected, actual, "no answer produced")
        if not isinstance(actual, (list, set, tuple)):
            return self._wrap(False, expected, actual,
                              f"actual must be a list/set, got {type(actual).__name__}")

        e_set, a_set = set(expected), set(actual)
        thr = self.config.jaccard_threshold

        if thr is None:
            passed = e_set == a_set
            missing = e_set - a_set
            extra = a_set - e_set
            reason = ("sets match exactly" if passed
                      else f"missing={sorted(missing)} extra={sorted(extra)}")
            return self._wrap(passed, sorted(e_set), sorted(a_set), reason)

        union = e_set | a_set
        jaccard = len(e_set & a_set) / len(union) if union else 1.0
        passed = jaccard >= thr
        reason = f"Jaccard={jaccard:.3f} >= {thr} -> {'pass' if passed else 'fail'}"
        return self._wrap(passed, sorted(e_set), sorted(a_set), reason, score=jaccard)
