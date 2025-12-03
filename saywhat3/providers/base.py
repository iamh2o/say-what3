"""Provider interfaces for running prompts against language models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Provider(Protocol):
    name: str

    def generate(self, prompt: str) -> str:
        """Generate a completion for a prompt."""
        raise NotImplementedError


@dataclass
class DummyProvider:
    """Deterministic provider useful for local testing and CI.

    It returns canned answers to the default prompts. Enable ``drift`` to
    intentionally return a wrong answer so score regression logic can be
    exercised without touching a real model API.
    """

    drift: bool = False
    name: str = "dummy"

    def generate(self, prompt: str) -> str:  # pragma: no cover - trivial
        normalized = prompt.lower()
        if "2 + 2" in normalized or "2+2" in normalized:
            return "5" if self.drift else "4"
        if "capital of france" in normalized:
            return "Paris"
        if "respond with the word" in normalized:
            return "yes"
        return "I am a stub provider."


__all__ = ["Provider", "DummyProvider"]
