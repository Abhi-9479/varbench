"""Claude agent: a tool-using loop over the Anthropic API.

Single agent class. Construct it once with a model + max_iters,
and __call__ it for each eval.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from varbench.agents.tools import TOOLS_SCHEMA, execute_bash, submit_answer

DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_MAX_ITERS = 15
DEFAULT_MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are a bioinformatics analysis agent.

You are given a task involving variant data files (VCF, TSV, etc.) and a
working directory containing those files. You have two tools:

1. `bash` - run shell commands in the working directory. Use it to
   inspect files (cat, head), parse them (grep, awk, wc, sort), or
   run quick Python scripts (python3 -c '...'). Prefer specific,
   small commands over reading whole files into context.

2. `submit_answer` - submit your final answer and end the task.
   The answer must be a JSON object whose keys exactly match what
   the task prompt asks for.

Rules:
- Actually inspect the data. Do not guess from prior knowledge.
- Be efficient. Each tool call costs time and tokens.
- When you are confident, call submit_answer once and stop.
- If the task is ambiguous, make the most reasonable interpretation
  and proceed - do not ask for clarification, there is no user to ask.
"""


class ClaudeAgent:
    """Tool-using agent backed by the Anthropic Messages API."""

    def __init__(self, model: str = DEFAULT_MODEL,
                 max_iters: int = DEFAULT_MAX_ITERS,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 verbose: bool = False) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package not installed. Run: pip install -e '.[agents]'"
            ) from e

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Export it or put it in .env."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.verbose = verbose

        # Diagnostics populated per run; useful for debugging in CLI.
        self.last_run: dict[str, Any] = {}

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def __call__(self, task_prompt: str, work_dir: Path) -> None:
        """Run the agent on one task. Populates work_dir/eval_answer.json."""
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": task_prompt},
        ]
        iters = 0
        submitted = False
        input_tokens = 0
        output_tokens = 0

        while iters < self.max_iters:
            iters += 1
            self._log(f"\n--- iter {iters} ---")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOLS_SCHEMA,
                messages=messages,
            )
            input_tokens += response.usage.input_tokens
            output_tokens += response.usage.output_tokens

            # Append the assistant turn verbatim.
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                # The model is done talking but didn't call submit_answer.
                # That's a soft failure; the runner will report "no answer".
                self._log(f"Stopped without submitting. stop_reason={response.stop_reason}")
                break

            # Execute each tool call in the assistant turn and build a
            # single user message containing all tool_result blocks.
            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                name = block.name
                tool_input = block.input or {}
                self._log(f"  tool={name}  input={tool_input}")

                if name == "bash":
                    result = execute_bash(tool_input.get("command", ""), work_dir)
                elif name == "submit_answer":
                    result = submit_answer(tool_input.get("answer", {}), work_dir)
                    submitted = True
                else:
                    result = f"<error>Unknown tool: {name}</error>"

                self._log(f"  result={result[:200]}{'...' if len(result) > 200 else ''}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

            if submitted:
                break

        self.last_run = {
            "iterations": iters,
            "submitted": submitted,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": self.model,
        }
