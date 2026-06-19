"""varbench command-line interface."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from varbench.agents import get_agent
from varbench.eval_spec import EvalSpec
from varbench.runner import EvalRunner

console = Console()


@click.group()
@click.version_option(package_name="varbench")
def main() -> None:
    """varbench: a benchmark for agentic variant analysis."""


@main.command()
@click.argument("eval_path", type=click.Path(exists=True, path_type=Path))
def validate(eval_path: Path) -> None:
    """Validate an evaluation JSON file against the schema."""
    try:
        spec = EvalSpec.from_json(eval_path)
    except Exception as e:
        console.print(f"[red]INVALID[/red] {eval_path}")
        console.print(f"  {e}")
        sys.exit(1)
    console.print(f"[green]VALID[/green]   {eval_path}")
    console.print(
        f"  id={spec.id}  category={spec.category.value}  "
        f"grader={spec.grader.type.value}  inputs={len(spec.inputs)}"
    )


@main.command()
@click.argument("eval_path", type=click.Path(exists=True, path_type=Path))
@click.option("--agent", default="echo", show_default=True,
              help="Agent: echo | null | claude")
@click.option("--model", default=None,
              help="Model string for LLM agents (e.g. claude-sonnet-4-5)")
@click.option("--work-dir", type=click.Path(path_type=Path), default=None,
              help="Working directory (default: results/runs/<eval-id>)")
@click.option("--save", type=click.Path(path_type=Path), default=None,
              help="If set, write the RunResult JSON to this path")
@click.option("--verbose", is_flag=True, help="Print agent's tool calls in real time")
def run(eval_path: Path, agent: str, model: str | None,
        work_dir: Path | None, save: Path | None, verbose: bool) -> None:
    """Run an evaluation with the chosen agent."""
    runner = EvalRunner(eval_path, work_dir=work_dir)

    if agent.lower() == "echo":
        agent_fn = get_agent(
            "echo",
            expected_answer=runner.spec.expected_answer,
            answer_key=runner.spec.answer_key,
        )
    else:
        agent_fn = get_agent(agent, model=model, verbose=verbose)

    result = runner.run(agent_fn, agent_name=agent)

    status = "[green]PASSED ✓[/green]" if result.passed else "[red]FAILED ✗[/red]"
    console.print(f"\n{status}  {result.eval_id}  ({result.elapsed_sec}s)")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("category", result.category)
    table.add_row("agent", result.agent)
    table.add_row("expected", repr(result.expected))
    table.add_row("actual", repr(result.actual))
    table.add_row("score", f"{result.score:.3f}")
    table.add_row("reason", result.reason)
    if result.error:
        table.add_row("[red]error[/red]", result.error)
    table.add_row("work_dir", result.work_dir)

    # If this was an LLM agent, surface token usage.
    if hasattr(agent_fn, "last_run") and agent_fn.last_run:
        lr = agent_fn.last_run
        table.add_row("iters", str(lr.get("iterations")))
        table.add_row("submitted", str(lr.get("submitted")))
        table.add_row("input_tokens", str(lr.get("input_tokens")))
        table.add_row("output_tokens", str(lr.get("output_tokens")))
        table.add_row("model", str(lr.get("model")))

    console.print(table)

    if save:
        save.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        if hasattr(agent_fn, "last_run"):
            payload["agent_meta"] = agent_fn.last_run
        save.write_text(json.dumps(payload, indent=2, default=str))
        console.print(f"\nSaved result to {save}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
