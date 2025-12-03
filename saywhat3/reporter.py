from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .results import ProbeResult, SuiteRun


def print_summary(run: SuiteRun) -> None:  # pragma: no cover - convenience wrapper
    summary = run.summary()
    print(f"Provider: {summary['provider']}")
    print(f"Pass rate: {summary['passed']}/{summary['total']} ({summary['pass_rate']*100:.0f}%)")
    print(f"Started:   {summary['started_at']}")
    print(f"Finished:  {summary['finished_at']}")
    print("\nPer-prompt results:")
    for result in run.results:
        status = "✅" if result.passed else "❌"
        print(f" {status} {result.prompt.id}: response='{result.response}' expected='{result.expected}'")


def write_jsonl(results: Iterable[ProbeResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for result in results:
            fh.write(json.dumps(result.as_dict(), ensure_ascii=False) + "\n")
