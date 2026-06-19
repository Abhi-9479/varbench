"""
Schema for a single varbench evaluation.

Mirrors the scbench format: each eval is a JSON file describing
one verifiable problem with task prompt, input data references,
expected answer, and grader configuration.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    VCF_QC = "vcf_qc"
    VARIANT_CALLING = "variant_calling"
    VARIANT_FILTERING = "variant_filtering"
    CLINICAL_INTERPRETATION = "clinical_interpretation"
    POPULATION_GENETICS = "population_genetics"
    DRUG_MOA = "drug_moa"


class GraderType(str, Enum):
    EXACT = "exact"               # exact string/int/bool match
    NUMERIC = "numeric"           # float within tolerance
    SET_MATCH = "set_match"       # set equality / Jaccard
    CATEGORICAL = "categorical"   # one of a fixed set of labels
    RUBRIC = "rubric"             # LLM-judge against a rubric


class InputFile(BaseModel):
    """A data file the agent has access to in its working directory."""
    path: str = Field(..., description="Filename inside the work_dir")
    source: str = Field(..., description="Where this file comes from (URL or relative path)")
    sha256: str | None = Field(None, description="Optional integrity check")
    description: str | None = None


class GraderConfig(BaseModel):
    """Grader-specific configuration. Shape depends on `type`."""
    type: GraderType
    # Common fields read by specific graders:
    tolerance: float | None = None              # numeric
    rel_tolerance: float | None = None          # numeric
    case_sensitive: bool = True                 # exact / categorical
    allowed_labels: list[str] | None = None     # categorical
    jaccard_threshold: float | None = None      # set_match (None = exact set)
    rubric: str | None = None                   # rubric
    judge_model: str | None = None              # rubric


class EvalSpec(BaseModel):
    """One varbench evaluation problem."""
    id: str = Field(..., description="Stable ID, e.g. 'vcf_qc_001_filter_pass_dp20'")
    category: Category
    subcategory: str | None = None
    title: str
    description: str = Field(..., description="Human-readable problem description")
    task_prompt: str = Field(..., description="The natural-language prompt given to the agent")
    inputs: list[InputFile] = Field(default_factory=list)
    answer_key: str = Field(
        ...,
        description="The key in eval_answer.json the agent must populate"
    )
    expected_answer: Any = Field(..., description="The correct value for `answer_key`")
    grader: GraderConfig
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: list[str] = Field(default_factory=list)
    version: str = "0.1.0"
    notes: str | None = None

    @field_validator("id")
    @classmethod
    def _id_format(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("id must be alphanumeric with _ or - only")
        return v

    @classmethod
    def from_json(cls, path: str | Path) -> "EvalSpec":
        import json
        return cls.model_validate_json(Path(path).read_text())

    def to_json(self, path: str | Path, indent: int = 2) -> None:
        Path(path).write_text(self.model_dump_json(indent=indent))
