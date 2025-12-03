from __future__ import annotations

import argparse
from pathlib import Path

from .prompts import load_prompts
from .providers.base import DummyProvider
from .reporter import print_summary, write_jsonl
from .runner import run_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the say-what3 probe suite")
    parser.add_argument("--provider", default="dummy", choices=["dummy"], help="Provider to use (default: dummy)")
    parser.add_argument("--drift", action="store_true", help="Return a wrong answer for math-addition to simulate regression")
    parser.add_argument("--output", type=Path, default=None, help="Path to write JSONL results")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.provider == "dummy":
        provider = DummyProvider(drift=args.drift)
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unknown provider: {args.provider}")

    prompts = load_prompts()
    run = run_suite(prompts, provider)

    print_summary(run)

    if args.output is not None:
        write_jsonl(run.results, args.output)
        print(f"\nWrote {len(run.results)} results to {args.output}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
