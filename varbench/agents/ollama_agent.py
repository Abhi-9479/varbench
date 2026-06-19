"""Ollama agent: same tool-using loop as ClaudeAgent, different SDK.

Uses Ollama's OpenAI-compatible chat-completions endpoint with tool calls.
Qwen-2.5 and Llama-3.1 8B both support function calling well enough for
this benchmark.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from varbench.agents.tools import TOOLS_SCHEMA, execute_bash, submit_answer

DEFAULT_MODEL = "qwen2.5:7b-instruct"
DEFAULT_MAX_ITERS = 15
DEFAULT_NUM_PREDICT = 1024  # ollama's max_tokens equivalent

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
- When you are confident, call submit_answer once and stop.
- If the task is ambiguous, make the most reasonable interpretation
  and proceed - do not ask for clarification.
- Follow the answer schema EXACTLY. If the prompt says the value must
  be one of three literal strings, write that exact string with no
  abbreviations.
"""


def _convert_tools_for_ollama(tools_schema: list) -> list:
    """Anthropic tools schema -> OpenAI/Ollama function-calling schema."""
    out = []
    for t in tools_schema:
        out.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        })
    return out


class OllamaAgent:
    """Tool-using agent backed by a local Ollama server."""

    def __init__(self, model: str = DEFAULT_MODEL,
                 max_iters: int = DEFAULT_MAX_ITERS,
                 num_predict: int = DEFAULT_NUM_PREDICT,
                 host: str | None = None,
                 verbose: bool = False) -> None:
        try:
            import ollama
        except ImportError as e:
            raise ImportError(
                "ollama package not installed. Run: pip install -e '.[agents]'"
            ) from e

        host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=host)
        self.model = model
        self.max_iters = max_iters
        self.num_predict = num_predict
        self.verbose = verbose
        self.tools = _convert_tools_for_ollama(TOOLS_SCHEMA)
        self.last_run: dict[str, Any] = {}

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def __call__(self, task_prompt: str, work_dir: Path) -> None:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_prompt},
        ]
        iters = 0
        submitted = False

        while iters < self.max_iters:
            iters += 1
            self._log(f"\n--- iter {iters} ---")

            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=self.tools,
                options={"temperature": 0.1, "num_predict": self.num_predict},
            )
            msg = response["message"]
            # Append the assistant turn verbatim.
            messages.append(msg)

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                # Model is done talking but didn't call submit_answer.
                self._log("Stopped without submitting.")
                break

            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                # Ollama returns arguments as a dict already (sometimes a string).
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}

                self._log(f"  tool={name}  input={args}")

                if name == "bash":
                    result = execute_bash(args.get("command", ""), work_dir)
                elif name == "submit_answer":
                    result = submit_answer(args.get("answer", {}), work_dir)
                    submitted = True
                else:
                    result = f"<error>Unknown tool: {name}</error>"

                self._log(f"  result={result[:200]}{'...' if len(result) > 200 else ''}")

                messages.append({
                    "role": "tool",
                    "content": result,
                })

            if submitted:
                break

        self.last_run = {
            "iterations": iters,
            "submitted": submitted,
            "input_tokens": None,   # Ollama does not return usage by default
            "output_tokens": None,
            "model": self.model,
        }
