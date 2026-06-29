# varbench

A benchmark for agentic variant analysis. varbench evaluates LLM agents on practical variant-interpretation workflows — VCF parsing, ACMG-style clinical classification, population-genetics threshold reasoning, and drug mechanism-of-action inference — using the format and methodology of [scbench](https://github.com/latchbio/scbench) and [spatialbench](https://github.com/latchbio/spatialbench).

Each problem pairs a small data snapshot (VCF, TSV, or evidence text) with a natural-language task prompt and a deterministic grader that maps the agent's structured output to pass/fail. Five grader families (exact, numeric, set_match, categorical, rubric) cover answer shapes from integer counts to free-text mechanism inferences.

## Status

v0.1 — initial release. 64 evaluations across six task categories. Two agents wired (Anthropic Claude, local Ollama). Results below are from the first end-to-end benchmarking pass.

## Install

```bash
git clone https://github.com/Abhi-9479/varbench
cd varbench
python3.11 -m venv venv && source venv/bin/activate
pip install -e ".[agents]"
export ANTHROPIC_API_KEY=sk-ant-...   # optional, for Claude agent
```

## Quickstart

```bash
# Validate one eval against the schema
varbench validate evals_canonical/vcf_qc/count_pass_variants.json

# Run one eval with a real agent
varbench run evals_canonical/vcf_qc/count_pass_variants.json \
    --agent claude --verbose

# Run all evals against an agent
for f in $(find evals_canonical evals_generated -name "*.json" \
            -not -name manifest.json); do
  varbench run "$f" --agent claude \
      --save "results/$(basename $f .json).json"
done

# Render a comparison leaderboard
varbench leaderboard \
    --model "Claude=results/claude_run" \
    --model "Qwen=results/qwen_run" \
    --out leaderboard.md
```

## Task categories

| Category | Count | Example |
| --- | --- | --- |
| `vcf_qc` | 2 | Count PASS variants; compute Ti/Tv ratio |
| `variant_calling` | 1 | List heterozygous variants as CHROM:POS:REF:ALT set |
| `variant_filtering` | 4 | PASS AND DP≥30; consequence retrieval; compound 4-way filter; VEP combined-annotation handling |
| `clinical_interpretation` | 52 | ACMG five-class classification (2 hand-authored canonical + 50 ClinVar-derived) |
| `population_genetics` | 1 | ACMG BA1 frequency-threshold check (PCSK9 R46L) |
| `drug_moa` | 4 | LOF → drug MoA inference (PCSK9 inhibitor, CETP unclear, with adversarial framings) |

## Results

### Headline

| Model | Score | Pass rate | Mean iterations |
| --- | --- | --- | --- |
| Claude Sonnet 4.5 (Anthropic API) | 39/64 | 60.9% | 4.1 |
| Qwen 2.5 7B Instruct (local Ollama) | 39/64 | 60.9% | 7.4 |

The two models tied on the overall pass rate. The category breakdown tells a more interesting story.

### By category

| Category | Claude Sonnet 4.5 | Qwen 2.5 7B |
| --- | --- | --- |
| `vcf_qc` | **2/2** | 0/2 |
| `variant_calling` | **1/1** | 0/1 |
| `variant_filtering` | **4/4**  | 1/4 |
| `population_genetics` | 1/1 | 1/1 |
| `drug_moa` |/4** | 2/4 |
| `clinical_interpretation` | 27/52 | **35/52** |

Claude wins or ties every category except `clinical_interpretation`, where it loses by 8 evals — enough to neutralize all its other wins. **Claude is stronger at empirical data-handling tasks. Qwen scores higher on categorical clinical-label prediction.**

### The clinical-interpretation result, in detail

We bulk-generated 50 clinical-interpretation evals from [NCBI ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/), filtering to 3-star (`reviewed by expert panel`) and 4-star (`practice guideline`) entries and sampling 10 variants per ACMG class (Pathogenic / Likely_pathogenic / Uncertain_significance / Likely_benign / Benign, random seed 42). The agent receives a small TSV with gene symbol, HGVS notation, genomic coordinates, variant type, and last-evaluated year — and must produce one of the five labels. Expected answers come directly from ClinVar's expert-panel consensus, so no hand-authored ground-truth bugs are possible.

On these 50 evals:
| Model | Strict pass rate | Partial-credit |
| --- | --- | --- |
| Claude Sonnet 4.5 | 25/50 (50.0%) | 34.5/50 (69.0%) |
| Qwen 2.5 7B | 33/50 (66.0%) | 36.0/50 (72.0%) |

Partial-credit gives half a point for an answer that is off by exactly one ACMG step (e.g. Benign → Likely_benign, or Pathogenic → Likely_pathogenic). Strict gives full credit only on exact match.

The strict gap is 16 points. The partial-credit gap is 3 points. **Most of Claude's "losses" are off-by-one hedges into adjacent ACMG categories.** Claude's verbose reasoning makes this explicit on case after case: when given a sparse TSV without population-frequency data, the model recognizes that the strongest benign criteria (ACMG BA1, BS1) cannot be applied and defaults to the less-committal label. Of Claude's 25 misses on the ClinVar set, 19 (76%) are exactly one ACMG step away from the consensus.

Qwen, by contrast, makes more aggressive commitments. Its top failure modes on the same 50 evals: Likely_benign → Pathogenic (×4), Benign → Pathogenic (×3), Likely_pathogenic → Pathogenic (×3). When its priors point in the right direction it wins; when they don't, it misses badly. On a benchmark that is itself stratified across pathogenic-heavy expert-panel review (Lynch syndrome and HBOC genes dominate ClinVar's 3-star entries), this aggressive-prior strategy happens to align with ground truth more often than careful uncertainty calibration does.

### Prompt-sensitivity ablation

To test whether Claude's hedging behavior could be reduced with prompt engineering, we A/B-tested two system prompts on the same 50 ClinVar evals — same model, same data files, same seed, only one sentence different.

| System prompt variant | Strict | Partial |
| --- | --- | --- |
| v1: "Inspect data; do not guess from prior knowledge" | 25/50 (50.0%) | 34.5/50 (69.0%) |
| v2: "Inspect data; for classification tasks you may apply domain knowledge; prefer the most specific defensible label" | 21/50 (42.0%) | 31.0/50 (62.0%) |

v2 was designed to reduce VUS-hedging by explicitly licensing prior knowledge and pushing toward specific labels. The result: the model over-corrected in the opposite direction, committing too readily to Pathogenic where Likely_pathogenic was correct (LP → P confusions rose). Net regression: ~7 partial-credit points.

**Finding: ACMG five-class classification is sensitive to prompt phrasing at the ±7 point scale.** "Help the model decide" framings trade one bias for another. Lifting accuracy here likely requires giving the model the actual missing data (population frequency from gnomAD) rather than further prompt tuning.

### Failure modes by category

On the seven data-parsing and filtering evals where Qwen failed but Claude passed, the failure modes break down as:

- **Premature submission without verification** (3 evals): Qwen called `submit_answer` after 1–2 tool calls without inspecting the data carefully. On `multi_condition_filter` it submitted on iteration 1 with `n_passing=15` (true answer: 2) without ever calling `bash`.
- **Wrong column reference** (`count_pass_variants`): Qwen ran `awk '$10 == "PASS"'` instead of `$7`, conflating SAMPLE1 genotype with FILTER status.
- **Tokenizer artifact in structured output** (`list_heterozygous_variants`): Qwen generated correct positions and alleles but its tokenizer encoded the `:A:` substring as U+1F170 (🅰), corrupting the output strings. The model knew the answer; it could not emit it under the required schema.

These failure modes are the kind of finding a benchmark should surface: they have clear remediation implications (Qwen needs more verification-encouraging prompts; the tokenizer issue is a known class of open-weight-model output-format failure that benchmarks should account for).

### Methodological notes

- **Bulk-generated evals catch authoring bugs.** During hand-authoring of canonical evals, one problem (`multi_condition_filter`) had a wrong hand-counted expected_answer (3 when the truth was 2). Claude correctly returned 2; the grader flagged the mismatch. Bulk generation from ClinVar's expert-panel data sidesteps this entirely — the expected_answer is the database's classification field, not a human-supplied number.
- **Prompt-template ambiguity masquerades as model failure.** An early drug_moa eval template used `{"moa": "<one of: a, b, c>"}`. Claude interpreted the angle-bracket form as a fill-in slot and submitted the abbreviation `"inhibit"`. Listing the allowed values as literal quoted strings ("a", "b", "c") fixed it.
- **Bash-as-side-channel.** Qwen 2.5 7B writes the final answer file directly via `echo > eval_answer.json` rather than calling the structured `submit_answer` tool in roughly half of its passing evals. The grader correctly grades the resulting file either way; the `submitted: False` flag in our run metadata signals this provenance.

## Known limitations

- **No population frequency in clinical_interpretation TSVs.** The 50 ClinVar evals do not include gnomAD allele frequency, which is the primary evidence underlying ACMG BA1 (allele frequency > 5% in any population) and BS1 (above expected for disease prevalence). A V2 release adding gnomAD AF is the natural next step and would isolate how much of the model accuracy gap is attributable to missing population data.
- **Pathogenic-heavy gene distribution.** ClinVar 3-star entries skew toward Lynch syndrome and HBOC genes (MLH1, MSH2, BRCA1, BRCA2, PMS2). Future versions should weight toward broader disease-gene coverage.
- **Possible memorization.** Famous pathogenic variants (e.g. BRCA1 c.68_69del) are in the training data of most modern LLMs. The benchmark cannot fully isolate reasoning from recall. Comparing scores against newly added 3-star variants (those added to ClinVar after model knowledge-cutoffs) is a planned mitigation.
- **No structural variants, copy-number variants, or non-coding regulatory variants.** v0.1 covers SNV/indel only.

## Eval format

Each eval is a single JSON file conforming to `varbench.eval_spec.EvalSpec`:

```json
{
  "id": "ci_clinvar_001_MLH1_89608",
  "category": "clinical_interpretation",
  "title": "Classify MLH1 variant (ClinVar VarID 89608)",
  "task_prompt": "You are given a TSV file at variant.tsv ...",
  "inputs": [
    {"path": "variant.tsv", "source": "data/variant_001.tsv"}
  ],
  "answer_key": "classification",
  "expected_answer": "Pathogenic",
  "grader": {
    "type": "categorical",
    "case_sensitive": true,
    "allowed_labels": ["Pathogenic", "Likely_pathogenic", "Uncertain_significance", "Likely_benign", "Benign"]
  }
}
```

The runner copies declared input files into a sandboxed work directory, invokes the agent, reads `eval_answer.json`, and grades against `expected_answer` using the configured grader. Agents see only the prompt and the work directory; they do not see the expected answer or the grader configuration.

## Reproducing the results

```bash
# Download ClinVar (~200MB)
mkdir -p data/clinvar && cd data/clinvar
curl -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
cd ../..

# Regenerate the 50 ClinVar evals (seeded; reproducible)
python scripts/generate_clinvar_evals.py --n 50 --seed 42 \
    --out evals_generated/clinical_interpretation

# Full Claude run (cost ~$2, ~25 minutes)
for f in $(find evals_canonical evals_generated -name "*.json" \
            -not -name manifest.json); do
  varbench run "$f" --agent claude --save \
      "results/claude/$(basename $f .json).json"
done

# Full Qwen run (free, ~30 minutes, requires ollama with qwen2.5:7b-instruct)
for f in $(find evals_canonical evals_generated -name "*.json" \
            -not -name manifest.json); do
  varbench run "$f" --agent ollama --save \
      "results/qwen/$(basename $f .json).json"
done

# Render leaderboard
varbench leaderboard \
    --model "Claude Sonnet 4.5=results/claude" \
    --model "Qwen 2.5 7B=results/qwen" \
    --out leaderboard.md
```

## License

Apache-2.0. See LICENSE.

## Acknowledgments

Format and methodology adapted from LatchBio's [scbench](https://github.com/latchbio/scbench) and [spatialbench](https://github.com/latchbio/spatialbench).
