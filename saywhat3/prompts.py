from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Prompt:
    """A single probe prompt with an optional expected answer for scoring."""

    id: str
    text: str
    expected: str | None = None


DEFAULT_PROMPTS: List[Prompt] = [
    Prompt(id="math-addition", text="What is 2 + 2?", expected="4"),
    Prompt(id="factual-capital", text="What is the capital of France?", expected="Paris"),
    Prompt(id="instruction-following", text="Respond with the word 'yes' exactly.", expected="yes"),
]


def load_prompts(custom_prompts: Iterable[Prompt] | None = None) -> List[Prompt]:
    """Return the supplied prompts or the built-in defaults."""

    if custom_prompts is None:
        return list(DEFAULT_PROMPTS)
    return list(custom_prompts)
