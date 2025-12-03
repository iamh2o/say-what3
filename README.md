# say-what3

Lightweight daily probing of AI model capabilities.

## What is this?

Say-What3 is a tiny, runnable prototype for tracking changes in large language model performance over time. It ships with a deterministic dummy provider so you can exercise the pipeline locally without API keys, plus clear seams to swap in real model clients later.

## How to run

The repo has no external dependencies. Use Python 3.11+ and run the suite via the CLI:

```bash
python -m saywhat3.main
```

You should see a summary of three built-in prompts. To simulate a regression (one wrong answer), toggle the drift flag:

```bash
python -m saywhat3.main --drift
```

To save results for downstream analysis, supply an output path. Each probe result is written as one JSON line containing the prompt, response, score, and timestamp:

```bash
python -m saywhat3.main --output runs/latest.jsonl
```

## How it works

- **Prompts** live in `saywhat3/prompts.py`. The defaults cover simple math, factual recall, and instruction following. Add more prompts or supply your own list to broaden coverage.
- **Providers** implement a `generate(prompt: str) -> str` method. `DummyProvider` returns canned answers so you can exercise the stack deterministically. Swap it with a real API client when you're ready.
- **Runner** in `saywhat3/runner.py` executes prompts against a provider, timestamps results, and performs case-insensitive exact-match scoring when an expected answer is present.
- **Reporter** in `saywhat3/reporter.py` prints a concise console summary and can persist JSONL artifacts.

The current prototype is intentionally minimal. It is designed to be scheduled from cron/CI, pointed at real providers, and extended with richer evaluators and alerting as you grow the prompt suite.
