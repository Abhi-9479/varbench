"""Bulk-generate varbench clinical-interpretation evals from ClinVar.

Filters ClinVar's variant_summary.txt.gz to expert-panel-reviewed
(3-star) and practice-guideline (4-star) entries, samples stratified
by ClinicalSignificance, and writes one eval JSON + one input TSV
per variant.

Run from the project root:
    python scripts/generate_clinvar_evals.py --n 50 --out evals_generated/clinical_interpretation
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

import pandas as pd

# ClinVar's ClinicalSignificance -> our 5 ACMG labels.
# We deliberately do NOT include "Conflicting interpretations of pathogenicity"
# or "Pathogenic/Likely pathogenic" combined entries - those are ambiguous
# ground truth and would muddy the eval signal.
SIG_MAP = {
    "Pathogenic": "Pathogenic",
    "Likely pathogenic": "Likely_pathogenic",
    "Uncertain significance": "Uncertain_significance",
    "Likely benign": "Likely_benign",
    "Benign": "Benign",
}

# Only accept 3-star and 4-star ClinVar entries as ground truth.
ACCEPTED_REVIEW_STATUS = {
    "reviewed by expert panel",
    "practice guideline",
}

# ClinVar variant types we keep. Excludes structural / copy-number /
# microsatellite which need different annotation framing.
ACCEPTED_TYPES = {
    "single nucleotide variant",
    "Deletion",
    "Duplication",
    "Insertion",
    "Indel",
}


def load_clinvar(path: Path) -> pd.DataFrame:
    """Read variant_summary.txt.gz and filter to high-confidence entries."""
    print(f"Reading {path} ...")
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    print(f"  raw rows: {len(df):,}")

    # Strict filters
    df = df[df["Assembly"] == "GRCh38"]
    df = df[df["ReviewStatus"].str.lower().isin(ACCEPTED_REVIEW_STATUS)]
    df = df[df["ClinicalSignificance"].isin(SIG_MAP.keys())]
    df = df[df["Type"].isin(ACCEPTED_TYPES)]
    # Require coordinate fields
    for col in ["Chromosome", "PositionVCF", "ReferenceAlleleVCF", "AlternateAlleleVCF"]:
        df = df[df[col].notna() & (df[col] != "") & (df[col] != "na")]
    # Require gene symbol
    df = df[df["GeneSymbol"].notna() & (df["GeneSymbol"] != "")]
    # Drop multi-gene rows (semicolon-separated) for cleaner per-eval framing
    df = df[~df["GeneSymbol"].str.contains(";", na=False)]

    print(f"  filtered: {len(df):,} high-confidence variants")
    return df.reset_index(drop=True)


def sample_stratified(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Sample n variants stratified across the 5 ACMG classes."""
    per_class = max(1, n // len(SIG_MAP))
    pieces = []
    for sig in SIG_MAP:
        sub = df[df["ClinicalSignificance"] == sig]
        take = min(per_class, len(sub))
        if take == 0:
            print(f"  WARNING: zero high-confidence entries for {sig}")
            continue
        pieces.append(sub.sample(n=take, random_state=seed))
        print(f"  {sig:<28} sampled {take} of {len(sub)}")
    return pd.concat(pieces).reset_index(drop=True)


def _slugify(s: str) -> str:
    """Make a string safe for use in a filename or eval ID."""
    return re.sub(r"[^A-Za-z0-9_]", "_", s)[:40]


def _last_evaluated_year(s: str) -> str:
    """Pull the year from a date like 'Jul 25, 2024' or '2024-07-25'."""
    if not isinstance(s, str):
        return "unknown"
    m = re.search(r"(19|20)\d{2}", s)
    return m.group(0) if m else "unknown"


def generate_eval(row: pd.Series, idx: int, out_dir: Path) -> dict | None:
    """Generate one eval JSON + TSV from a ClinVar row. Returns the eval dict or None on error."""
    try:
        gene = row["GeneSymbol"]
        hgvs = row["Name"]
        chrom = row["Chromosome"]
        pos = row["PositionVCF"]
        ref = row["ReferenceAlleleVCF"]
        alt = row["AlternateAlleleVCF"]
        vtype = row["Type"]
        sig = row["ClinicalSignificance"]
        review = row["ReviewStatus"]
        variation_id = row["VariationID"]
        last_eval = _last_evaluated_year(row.get("LastEvaluated", ""))
    except KeyError as e:
        print(f"  [{idx:03d}] missing field: {e}")
        return None

    expected = SIG_MAP[sig]
    eval_id = f"ci_clinvar_{idx:03d}_{_slugify(gene)}_{variation_id}"

    # Write the input TSV.
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    tsv_name = f"variant_{idx:03d}.tsv"
    tsv_path = data_dir / tsv_name
    tsv_rows = [
        "field\tvalue",
        f"gene\t{gene}",
        f"hgvs\t{hgvs}",
        f"chrom\t{chrom}",
        f"pos\t{pos}",
        f"ref\t{ref}",
        f"alt\t{alt}",
        f"variant_type\t{vtype}",
        f"last_evaluated_year\t{last_eval}",
        "annotation_source\tNCBI ClinVar",
    ]
    tsv_path.write_text("\n".join(tsv_rows) + "\n")

    # Build the eval JSON.
    eval_dict = {
        "id": eval_id,
        "category": "clinical_interpretation",
        "subcategory": "clinvar_high_confidence_classification",
        "title": f"Classify {gene} variant (ClinVar VarID {variation_id})",
        "description": (
            f"Classify a single variant in {gene} using its HGVS notation, "
            f"coordinates, and variant type. Ground truth is ClinVar's "
            f"{review} consensus classification ({sig})."
        ),
        "task_prompt": (
            "You are given a TSV file at variant.tsv in your working directory. "
            "It is a two-column 'field\\tvalue' table describing a single human "
            "genetic variant: gene, HGVS notation, genomic coordinates, ClinVar "
            "variant type, and provenance. Based on these fields and standard "
            "ACMG/AMP interpretation principles, assign the variant exactly one "
            "classification. Write your answer as JSON to eval_answer.json with "
            "this exact schema: {\"classification\": \"<value>\"}, where <value> "
            "must be the literal string \"Pathogenic\", \"Likely_pathogenic\", "
            "\"Uncertain_significance\", \"Likely_benign\", or \"Benign\" - "
            "written exactly as shown including the underscore."
        ),
        "inputs": [
            {
                "path": "variant.tsv",
                "source": f"data/{tsv_name}",
                "description": f"Annotations for {gene} {hgvs}",
            }
        ],
        "answer_key": "classification",
        "expected_answer": expected,
        "grader": {
            "type": "categorical",
            "case_sensitive": True,
            "allowed_labels": list(SIG_MAP.values()),
        },
        "difficulty": "medium",
        "tags": [
            "clinvar",
            "acmg",
            "auto_generated",
            _slugify(gene).lower(),
            expected.lower(),
        ],
        "version": "0.1.0",
        "notes": (
            f"Auto-generated from ClinVar VariationID={variation_id}, "
            f"ReviewStatus='{review}', ClinicalSignificance='{sig}'. "
            f"V1 limitation: no gnomAD AF or in-silico predictions in TSV. "
            f"The agent must infer molecular consequence from HGVS notation."
        ),
    }

    json_path = out_dir / f"{eval_id}.json"
    json_path.write_text(json.dumps(eval_dict, indent=2))
    return eval_dict


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clinvar", default="data/clinvar/variant_summary.txt.gz",
                    type=Path, help="Path to ClinVar variant_summary.txt.gz")
    ap.add_argument("--n", type=int, default=50, help="Number of evals to generate")
    ap.add_argument("--out", type=Path, default=Path("evals_generated/clinical_interpretation"),
                    help="Output directory for evals + data")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    df = load_clinvar(args.clinvar)
    sample = sample_stratified(df, n=args.n, seed=args.seed)
    print(f"\nGenerating {len(sample)} evals into {args.out} ...")

    generated = 0
    for idx, (_, row) in enumerate(sample.iterrows(), start=1):
        result = generate_eval(row, idx, args.out)
        if result:
            generated += 1
            if idx <= 5 or idx % 10 == 0:
                print(f"  [{idx:03d}] {result['id']:<50} -> {result['expected_answer']}")

    # Write a manifest summary.
    manifest = {
        "n_generated": generated,
        "n_requested": args.n,
        "by_class": sample["ClinicalSignificance"].value_counts().to_dict(),
        "by_review_status": sample["ReviewStatus"].value_counts().to_dict(),
        "clinvar_file": str(args.clinvar),
        "seed": args.seed,
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nDone. {generated} evals generated. Manifest: {args.out}/manifest.json")


if __name__ == "__main__":
    main()
