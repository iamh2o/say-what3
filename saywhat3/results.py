from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from .prompts import Prompt


@dataclass
class ProbeResult:
    prompt: Prompt
    response: str
    expected: str | None
    score: float
    passed: bool
    run_at: datetime

    def as_dict(self) -> dict:
        return {
            "id": self.prompt.id,
            "prompt": self.prompt.text,
            "response": self.response,
            "expected": self.expected,
            "score": self.score,
            "passed": self.passed,
            "run_at": self.run_at.isoformat(),
        }


@dataclass
class SuiteRun:
    provider_name: str
    results: List[ProbeResult]
    started_at: datetime
    finished_at: datetime

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        return {
            "provider": self.provider_name,
            "passed": passed,
            "total": total,
            "pass_rate": passed / total if total else 0.0,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
        }

    def as_dict(self) -> dict:
        return {"summary": self.summary(), "results": [r.as_dict() for r in self.results]}
