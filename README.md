# varbench

Benchmark for agentic variant analysis.

varbench evaluates AI agents on practical variant-interpretation workflows: VCF QC,
variant filtering, clinical interpretation (ACMG/AMP), population genetics, and
drug mechanism-of-action reasoning. Each problem pairs a data snapshot with a
natural-language task prompt and a deterministic grader.

Format and methodology follow [scbench](https://github.com/latchbio/scbench) and
[spatialbench](https://github.com/latchbio/spatialbench).

## Status

🚧 Early development. See `evals_canonical/` for the eval format.

## Install

```bash
pip install -e .
```

## Quickstart

```bash
# Validate an evaluation
varbench validate evals_canonical/vcf_qc/example.json

# Run with an agent (Day 2+)
varbench run evals_canonical/vcf_qc/example.json --agent minisweagent --model anthropic/claude-sonnet-4-5
```

## Task categories

| Category | Example |
| --- | --- |
| `vcf_qc` | Filter to PASS variants with DP≥20 and GQ≥30. How many rema| `variant_calling` | List all het variants in gene X as `CHROM:POS:REF:ALT`. |
| `variant_filtering` | Apply gnomAD AF<0.01. Which variants pass? |
| `clinical_interpretation` | Classify this BRCA1 variant using ACMG criteria. |
| `population_genetics` | Given gnomAD AF for this variant, does it meet BA1? |
| `drug_moa` | PCSK9 p.R46L is a LoF variant. What drug MoA does this support? |

## License

Apache-2.0.
