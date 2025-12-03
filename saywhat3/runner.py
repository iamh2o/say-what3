from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List

from .prompts import Prompt
from .providers.base import Provider
from .results import ProbeResult, SuiteRun


def score_response(response: str, expected: str | None) -> float:
    if expected is None:
        return 0.0
    normalized_response = response.strip().lower()
    normalized_expected = expected.strip().lower()
    return 1.0 if normalized_response == normalized_expected else 0.0


def run_suite(prompts: Iterable[Prompt], provider: Provider) -> SuiteRun:
    started_at = datetime.now(timezone.utc)
    results: List[ProbeResult] = []

    for prompt in prompts:
        response = provider.generate(prompt.text)
        score = score_response(response, prompt.expected)
        run_at = datetime.now(timezone.utc)
        results.append(
            ProbeResult(
                prompt=prompt,
                response=response,
                expected=prompt.expected,
                score=score,
                passed=score >= 1.0,
                run_at=run_at,
            )
        )

    finished_at = datetime.now(timezone.utc)
    return SuiteRun(provider_name=getattr(provider, "name", provider.__class__.__name__), results=results, started_at=started_at, finished_at=finished_at)
