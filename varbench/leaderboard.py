"""Generate a leaderboard report from one or more results directories."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_run(directory: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(Path(directory).glob("*.json")):
        try:
            r = json.loads(p.read_text())
        except Exception:
            continue
        eid = r.get("eval_id")
        if eid:
            out[eid] = r
    return out


def summarize(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    passed = sum(1 for r in records.values() if r.get("passed"))
    by_cat: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    iters: list[int] = []
    in_tok = 0
    out_tok = 0
    for r in records.values():
        cat = r.get("category", "unknown")
        by_cat[cat][1] += 1
        if r.get("passed"):
            by_cat[cat][0] += 1
        meta = r.get("agent_meta") or {}
        if meta.get("iterations") is not None:
            iters.append(meta["iterations"])
        if meta.get("input_tokens"):
            in_tok += meta["input_tokens"]
        if meta.get("output_tokens"):
            out_tok += meta["output_tokens"]
    return {
        "total": total,
        "passed": passed,
        "pass_rate": passed / total if total else 0.0,
        "by_category": dict(by_cat),
        "mean_iters": sum(iters) / len(iters) if iters else None,
        "total_input_tokens": in_tok or None,
        "total_output_tokens": out_tok or None,
    }


def render_markdown(model_runs: dict[str, dict[str, dict[str, Any]]]) -> str:
    all_ids = sorted({eid for recs in model_runs.values() for eid in recs})
    models = list(model_runs.keys())
    lines = ["# varbench leaderboard\n", "## Headline\n"]
    lines.append("| Model | Score | Pass rate | Mean iters | Input tokens | Output tokens |")
    lines.append("|---|---|---|---|---|---|")
    for m in models:
        s = summarize(model_runs[m])
        score = f"{s['passed']}/{s['total']}"
        rate = f"{s['pass_rate']*100:.1f}%"
        it = f"{s['mean_iters']:.1f}" if s["mean_iters"] is not None else "-"
        it_t = str(s["total_input_tokens"]) if s["total_input_tokens"] else "-"
        ot_t = str(s["total_output_tokens"]) if s["total_output_tokens"] else "-"
        lines.append(f"| {m} | {score} | {rate} | {it} | {it_t} | {ot_t} |")
    lines.append("\n## By category\n")
    cats = sorted({c for m in models for c in summarize(model_runs[m])["by_category"]})
    lines.append("| Category | " + " | ".join(models) + " |")
    lines.append("|" + "|".join(["---"] * (len(models) + 1)) + "|")
    for c in cats:
        cells = [c]
        for m in models:
            bc = summarize(model_runs[m])["by_category"].get(c, [0, 0])
            cells.append(f"{bc[0]}/{bc[1]}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("\n## Per-eval results\n")
    lines.append("| eval_id | " + " | ".join(models) + " |")
    lines.append("|" + "|".join(["---"] * (len(models) + 1)) + "|")
    for eid in all_ids:
        cells = [f"`{eid}`"]
        for m in models:
            r = model_runs[m].get(eid)
            cells.append("—" if r is None else ("✅" if r["passed"] else "❌"))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("\n## Failure details\n")
    for m in models:
        fails = [(eid, r) for eid, r in model_runs[m].items() if not r["passed"]]
        if not fails:
            lines.append(f"### {m}\n_No failures._\n")
            continue
        lines.append(f"### {m}\n")
        for eid, r in fails:
            lines.append(f"- **`{eid}`**")
            lines.append(f"  - expected: `{r.get('expected')!r}`")
            lines.append(f"  - actual:   `{r.get('actual')!r}`")
            lines.append(f"  - reason:   {(r.get('reason') or '').strip()}")
        lines.append("")
    return "\n".join(lines)
