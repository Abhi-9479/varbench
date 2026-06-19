"""Tools that LLM agents call during the eval loop.

For now: one tool that runs bash in the work_dir (so the agent can
parse VCFs, grep, awk, write Python scripts), and one tool to submit
the final answer.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

# How long any single bash command may run before we kill it.
BASH_TIMEOUT_SEC = 30
# How much output we return to the model per call (anything bigger gets truncated).
BASH_MAX_OUTPUT_CHARS = 8000


def execute_bash(command: str, work_dir: Path) -> str:
    """Run `command` inside `work_dir` and return a formatted result string."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=BASH_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return f"<error>Command timed out after {BASH_TIMEOUT_SEC}s</error>"
    except Exception as e:
        return f"<error>Failed to run command: {type(e).__name__}: {e}</error>"

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    def _truncate(s: str, label: str) -> str:
        if len(s) > BASH_MAX_OUTPUT_CHARS:
            return s[:BASH_MAX_OUTPUT_CHARS] + f"\n...[{label} truncated]"
        return s

    parts = [f"exit_code: {proc.returncode}"]
    if stdout.strip():
        parts.append("stdout:\n" + _truncate(stdout, "stdout"))
    if stderr.strip():
        parts.append("stderr:\n" + _truncate(stderr, "stderr"))
    if not stdout.strip() and not stderr.strip():
        parts.append("(no output)")
    return "\n\n".join(parts)


def submit_answer(answer: dict[str, Any], work_dir: Path) -> str:
    """Write the answer to eval_answer.json and confirm."""
    if not isinstance(answer, dict):
        return f"<error>answer must be a JSON object, got {type(answer).__name__}</error>"
    out_path = work_dir / "eval_answer.json"
    try:
        out_path.write_text(json.dumps(answer, indent=2))
    except Exception as e:
        return f"<error>Failed to write eval_answer.json: {e}</error>"
    return f"Answer submitted: {json.dumps(answer)}"


# The JSON-schema tool definitions sent to the model.
TOOLS_SCHEMA = [
    {
        "name": "bash",
        "description": (
            "Run a shell command inside the working directory. "
            "The working directory contains the input files for this task. "
            "Use this to inspect files (cat, head, less), parse them "
            "(grep, awk, wc, sort, uniq), or run small Python snippets "
            "(python3 -c '...'). Each call is a fresh subprocess; "
            "state does not persist between calls. Output longer than "
            f"{BASH_MAX_OUTPUT_CHARS} characters is truncated."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "submit_answer",
        "description": (
            "Submit the final answer as a JSON object and end the task. "
            "The object's keys must match what the task prompt asks for. "
            "Calling this writes eval_answer.json. Call it exactly once "
            "when you are confident in your answer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "object",
                    "description": (
                        "The answer as a JSON object. For example, "
                        '{"n_pass": 6} or {"variants": ["chr1:1000:A:T", ...]}.'
                    ),
                },
            },
            "required": ["answer"],
        },
    },
]
