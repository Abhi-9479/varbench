"""Grader registry: maps GraderType -> Grader implementation."""
from __future__ import annotations

from varbench.eval_spec import GraderConfig, GraderType
from varbench.graders.base import Grader, GraderResult
from varbench.graders.categorical import CategoricalGrader
from varbench.graders.exact import ExactGrader
from varbench.graders.numeric import NumericGrader
from varbench.graders.rubric import RubricGrader
from varbench.graders.set_match import SetMatchGrader

_REGISTRY: dict[GraderType, type[Grader]] = {
    GraderType.EXACT: ExactGrader,
    GraderType.NUMERIC: NumericGrader,
    GraderType.SET_MATCH: SetMatchGrader,
    GraderType.CATEGORICAL: CategoricalGrader,
    GraderType.RUBRIC: RubricGrader,
}


def get_grader(config: GraderConfig) -> Grader:
    """Return an instantiated grader for the given config."""
    try:
        cls = _REGISTRY[config.type]
    except KeyError as e:
        raise ValueError(f"Unknown grader type: {config.type}") from e
    return cls(config)


__all__ = ["Grader", "GraderResult", "get_grader"]
