# CLAUDE.md - AI Assistant Guide for say-what3

## Project Overview

**say-what3** is a proposal and design document for a **Continuous Daily Probing System** that monitors AI model capabilities over time. The goal is to detect performance regressions or capability changes in AI models (GPT-4, Claude, Grok, etc.) through systematic daily evaluation.

### Motivation
Address concerns about AI providers potentially "dialing down" model capabilities. Studies have shown significant accuracy drops (e.g., GPT-4's accuracy dropping from 84% to 51% on certain tasks between March and June 2023).

### Current State
**This repository is at the proposal stage** - it contains only design documentation (README.md) with no implementation code yet.

---

## Repository Structure

```
say-what3/
├── README.md          # Comprehensive proposal document (~300 lines)
├── CLAUDE.md          # This file - AI assistant guide
└── .git/              # Git version control
```

### Future Planned Structure (When Implemented)

```
say-what3/
├── src/
│   ├── scheduler/           # Cron/job scheduler for daily runs
│   ├── executor/            # Prompt suite executor
│   ├── interfaces/          # Model interface adapters
│   │   ├── openai.py        # OpenAI GPT-3.5/GPT-4 API
│   │   ├── anthropic.py     # Anthropic Claude API
│   │   ├── grok.py          # xAI Grok (web automation)
│   │   └── base.py          # Base interface class
│   ├── evaluation/          # Scoring and evaluation module
│   ├── analyzer/            # Trend analysis and reporting
│   └── storage/             # Logging and data storage
├── prompts/
│   ├── logical_reasoning/   # Logic puzzles, math problems
│   ├── code_synthesis/      # Code generation and debugging
│   ├── factual_knowledge/   # Trivia, domain expertise
│   ├── multi_step/          # Multi-instruction tasks
│   ├── stylistic/           # Style and tone tests
│   ├── memory_context/      # Context handling tests
│   └── creativity/          # Creative reasoning prompts
├── tests/                   # Test suite
├── data/                    # Historical results storage
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Proposed System Architecture

### Modular Components

| Component | Purpose |
|-----------|---------|
| **Scheduler** | Triggers daily test suites via cron or GitHub Actions |
| **Prompt Suite Executor** | Loads and distributes benchmark prompts across platforms |
| **Model Interfaces** | Adapter modules for each AI platform (API or web UI) |
| **Evaluation Module** | Scores responses according to defined rubrics |
| **Trend Analyzer & Reporter** | Detects regressions and generates alerts/reports |
| **Logging & Storage** | Records raw outputs, metadata, and metrics |

### Target Platforms

1. **OpenAI ChatGPT** - GPT-3.5, GPT-4 via API
2. **Anthropic Claude** - Claude 2, Claude Instant via API
3. **xAI Grok** - Web automation (no public API)
4. **Google Bard** - Web interface
5. **Microsoft Bing Chat** - Web interface
6. **Open-Source Models** - Local LLaMA-2, etc. (as baseline control)

---

## Capability Domains to Evaluate

### 1. Logical Reasoning
- Symbolic logic puzzles (syllogisms, conditionals)
- Math word problems (multi-step arithmetic)
- Commonsense reasoning scenarios

### 2. Code Synthesis & Debugging
- Function implementation with test cases
- Bug fixing exercises
- Edge-case handling

### 3. Factual Knowledge & Domain Expertise
- Static trivia questions
- Time-stamped current events
- Niche domain questions

### 4. Multi-step Instruction Follow-Through
- Composite multi-task prompts
- Interactive multi-turn conversations
- Chain-of-thought reasoning

### 5. Stylistic Fluency & Consistency
- Style mimicry (Shakespeare, technical, etc.)
- Persona/tone maintenance
- Format compliance (limerick, JSON, etc.)

### 6. Memory & Context Handling
- Long-context recall
- Conversation consistency
- Context limit stress tests

### 7. Creativity & Analogical Reasoning
- Analogy and metaphor generation
- Concept blending challenges
- Creative problem solving

---

## Development Guidelines

### When Implementing This System

#### Technology Stack (Recommended)
- **Language**: Python 3.10+
- **APIs**: OpenAI SDK, Anthropic SDK
- **Web Automation**: Playwright or Selenium (for web-only platforms)
- **Data Storage**: SQLite/PostgreSQL or simple JSONL/CSV
- **Scheduling**: GitHub Actions, cron, or APScheduler
- **Visualization**: Matplotlib, Plotly, or web dashboard

#### Key Design Principles

1. **Determinism & Repeatability**
   - Use temperature=0 for deterministic outputs
   - Fix random seeds where supported
   - Run at consistent times daily
   - Store exact prompt text and parameters

2. **Modularity**
   - Each platform gets its own interface adapter
   - Evaluation rubrics are separate from data collection
   - Prompts are versioned and stored externally

3. **Lightweight Operation**
   - Minimal prompt set to keep costs low (~$5/day target)
   - Stream responses when possible
   - Can run on small VM or GitHub Actions

4. **Version Tracking**
   - Log model version strings (e.g., gpt-4-0613)
   - Store raw outputs with timestamps
   - Track prompt suite versions separately

#### Scoring Rubrics

| Dimension | Scoring Method |
|-----------|----------------|
| Logical Reasoning | Binary correct/incorrect, partial credit for method |
| Code Generation | % test cases passed, functional correctness |
| Factual Knowledge | Exact match or semantic similarity |
| Multi-step | Count of sub-tasks completed correctly |
| Stylistic | LLM-as-judge score (1-10) + format checks |
| Memory & Context | Binary success/failure on recall |
| Creativity | LLM-as-judge originality score (1-5) |

---

## Implementation Roadmap

When implementing, follow these phases:

1. **Prototype with One Model** - Core pipeline with OpenAI GPT-4
2. **Expand Prompt Catalog & Models** - Add Claude, other platforms
3. **Automate Scoring & Verification** - Evaluation scripts per prompt type
4. **Data Storage & Dashboard** - CSV/DB logging, basic reporting
5. **Establish Baseline & Thresholds** - Run for weeks to gather metrics
6. **Incorporate Version Control & Diffing** - Track model version changes
7. **Trial Run of Adversarial Cases** - Test edge cases and stress tests
8. **Deploy Scheduling & Notifications** - Production deployment
9. **Ongoing Maintenance** - Monitor, update prompts, refine thresholds

---

## Conventions for AI Assistants

### When Working on This Project

1. **Understand the Proposal First**
   - Read README.md thoroughly before implementing
   - The README contains detailed specifications for each component

2. **Prioritize Modularity**
   - Each model interface should be a separate, pluggable module
   - Evaluation logic should be decoupled from data collection

3. **Handle API Keys Securely**
   - Never hardcode API keys
   - Use environment variables or secure config files
   - Add `.env` to `.gitignore`

4. **Maintain Backward Compatibility**
   - When updating prompt suites, version them
   - Run old and new prompts in parallel during transitions
   - Document any changes that affect historical comparisons

5. **Focus on Reproducibility**
   - All parameters should be configurable
   - Log everything needed to reproduce a run
   - Use fixed seeds and deterministic settings

6. **Cost Awareness**
   - Keep the prompt set minimal but representative
   - Track API costs per run
   - Implement rate limiting to avoid overages

7. **Ethical Considerations**
   - Prefer official APIs over web scraping
   - Handle adversarial/edge-case outputs responsibly
   - Don't design prompts that violate platform ToS

### Code Style (When Implemented)

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Write docstrings for public functions
- Include unit tests for evaluation logic
- Use descriptive variable names

---

## Quick Reference

### Key Files
| File | Purpose |
|------|---------|
| `README.md` | Full proposal with architecture, prompts, and implementation plan |
| `CLAUDE.md` | This guide for AI assistants |

### Useful Commands (Future)
```bash
# Run daily probe (when implemented)
python -m src.scheduler run

# Run evaluation on stored results
python -m src.evaluation score --date 2024-01-15

# Generate trend report
python -m src.analyzer report --days 30

# Run tests
pytest tests/
```

### Environment Variables (Planned)
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///data/results.db
ALERT_EMAIL=alerts@example.com
```

---

## Related Resources

- DailyBench project (similar concept): Runs 4 evals/day at ~$5/day cost
- LLM evaluation best practices
- OpenAI API documentation
- Anthropic API documentation

---

## Contributing

When contributing to this project:

1. Create feature branches from main
2. Write tests for new evaluation logic
3. Document any new prompt types or scoring rubrics
4. Update this CLAUDE.md if architecture changes significantly
5. Keep commits atomic and well-described
