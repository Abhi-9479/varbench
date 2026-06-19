"""EvalRunner: orchestrates one eval end-to-end.

Loads spec -> stages input files into work_dir -> invokes agent ->
reads eval_answer.json -> grades -> returns RunResult.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from varbench.eval_spec import EvalSpec
from varbench.graders import GraderResult, get_grader

# Type for any agent function: takes (task_prompt, work_dir), populates
# work_dir / "eval_answer.json", and returns whatever (we ignore it).
AgentFn = Callable[[str, Path], Any]


@dataclass
class RunResult:
    """Outcome of running one eval with one agent."""
    eval_id: str
    category: str
    agent: str
    passed: bool
    score: float
    reason: str
    expected: Any
    actual: Any
    elapsed_sec: float
    work_dir: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvalRunner:
    """Run one EvalSpec against an agent function and grade the result."""

    ANSWER_FILE = "eval_answer.json"

    def __init__(self, spec_path: str | Path, work_dir: str | Path | None = None) -> None:
        self.spec_path = Path(spec_path).resolve()
        self.spec = EvalSpec.from_json(self.spec_path)
        self.work_dir = Path(work_dir) if work_dir else Path("results/runs") / self.spec.id
        self.work_dir = self.work_dir.resolve()

    def setup(self) -> None:
        """Create work_dir and stage input files for the agent."""
        self.work_dir.mkdir(parents=True, exist_ok=True)
        spec_dir = self.spec_path.parent
        for inp in self.spec.inputs:
            src = (spec_dir / inp.source).resolve()
            if not src.exists():
                raise FileNotFoundError(
                    f"Input file not found: {src} (referenced by {self.spec_path})"
                )
            dst = self.work_dir / inp.path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)

    def _read_answer(self) -> dict[str, Any]:
        path = self.work_dir / self.ANSWER_FILE
        if not path.exists():
            raise FileNotFoundError(
                f"Agent did not produce {self.ANSWER_FILE} in {self.work_dir}"
            )
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"{self.ANSWER_FILE} is not valid JSON: {e}") from e

    def run(self, agent_function: AgentFn, agent_name: str = "custom") -> RunResult:
        """Execute one eval: setup -> agent -> grade."""
        t0 = time.time()
        error: str | None = None
        passed = False
        score = 0.0
        reason = ""
        actual: Any = None

        try:
            self.setup()
            agent_function(self.spec.task_prompt, self.work_dir)
            answer = self._read_answer()
            actual = answer.get(self.spec.answer_key)

            grader = get_grader(self.spec.grader)
            result: GraderResult = grader.grade(self.spec.expected_answer, actual)
            passed, score, reason = result.passed, result.score, result.reason
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            reason = error

        return RunResult(
            eval_id=self.spec.id,
            category=self.spec.category.value,
            agent=agent_name,
            passed=passed,
            score=score,
            reason=reason,
            expected=self.spec.expected_answer,
            actual=actual,
            elapsed_sec=round(time.time() - t0, 3),
            work_dir=str(self.work_dir),
            error=error,
        )
