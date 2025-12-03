# say-what3
Proposal: Continuous Daily Probing of AI Model Capabilities
Introduction

AI users have observed instances where a model’s performance seems to decline over time, sparking concern that providers may be “dialing down” capabilities. For example, one study found GPT‑4’s accuracy on certain tasks (math problem solving, code generation) dropped from 84% to 51% between March and June 2023
ignorance.ai
. To systematically track such changes, we propose a daily evaluation program that probes multiple AI platforms (e.g. OpenAI’s ChatGPT, Anthropic’s Claude, xAI’s Grok, etc.) across key intellectual dimensions. The goal is to detect regressions or shifts in reasoning, coding, knowledge, and other skills promptly. This decision brief outlines a modular architecture for daily probing, a catalog of benchmark prompts per capability, scoring methodologies, platform coverage, and strategies for long-term version tracking and stress-testing.

System Architecture for Daily Probing

Figure: Proposed modular architecture for daily LLM capability probing. A scheduler triggers daily test suites across multiple model interfaces (via API or web automation). Each model’s responses to a fixed prompt set are evaluated and logged. An analyzer compares daily results to detect regressions, with reports/alerts generated from trends.

Modular Components: The system comprises several loosely coupled modules orchestrated by a scheduler:

Scheduler: A lightweight cron or job scheduler triggers the probe run once per day (or multiple times per day if higher frequency is needed). This ensures regular, time-stamped evaluations.

Prompt Suite Executor: This core module loads a predefined suite of benchmark prompts and iterates through each target AI platform. It dispatches each prompt to the appropriate platform interface (API call or web interaction). The design is modular, with a plugin/adapter for each platform (e.g., one for OpenAI API, one for Anthropic API, one for a web UI like Grok’s interface). This allows easy addition or removal of platforms.

Model Interfaces: For each platform, the system uses either an official API endpoint (preferred when available) or a public web UI harness. For APIs, the module will call the model with controlled parameters (e.g. temperature, max tokens). For web-only models, a headless browser or script mimics user queries (with proper rate limiting to avoid abuse). Each interface module handles authentication and formatting peculiarities of that platform.

Streaming & Lightweight Operation: The probes are designed to be lightweight – only a limited number of prompts are sent daily to minimize cost and complexity. If a model supports streaming responses, the system can stream-read the output to log partial progress (this helps if we want to detect if the model stalls or truncates answers). However, final evaluation is done on the complete response. The entire pipeline can run on a small VM or even as a GitHub Actions workflow, since it’s not resource-intensive (e.g., DailyBench, an open project, runs 4 small evals per day at ~$5/day cost
github.com
github.com
).

Logging & Storage: All raw outputs from each model, along with metadata (model name, version if available, timestamp, prompt ID) are recorded. This could be as simple as appending to a JSONL or CSV log file, or inserting into a database. Version metadata is crucial – e.g., if the API returns a model version string (like GPT-4-0613), it is stored to correlate performance changes with model updates.

Evaluation Module: Once responses are collected, an automatic evaluator module scores each response according to the rubrics (described in the next section). This yields quantitative metrics per prompt per model (e.g. correctness = true/false, score = 7/10, etc.).

Trend Analyzer & Reporter: The day’s results are then compared with historical data. The analyzer computes diffs and trends – for example, changes in success rate or output length compared to the past week’s average. It can flag significant deviations beyond a preset threshold. The system then produces a report (e.g. an emailed summary or a dashboard update) highlighting any capability drops or notable changes. Over time, a dashboard can visualize these trends (similar to how DailyBench plots model performance over time
github.com
github.com
).

Determinism and Repeatability: To attribute changes to the model (and not randomness), the system controls variability tightly. All prompts are fixed in wording and order each day, and API parameters are set for deterministic behavior (temperature 0 or low, fixed random seed if supported)
github.com
. This way, under identical conditions a stable model should yield consistent outputs. Minor day-to-day variance is possible (especially for non-deterministic outputs or if the model does internal sampling), but the system isn’t looking at one-off differences – it looks for clear, repeated patterns of regression
github.com
. Running the evaluation at the same time daily (or uniformly across times) controls for any diurnal effects or load variance. If needed, multiple runs per day can be scheduled to sample different times (DailyBench runs 4× daily to catch peak vs off-peak differences
github.com
). All runs are logged for longitudinal analysis.

Rationale: This architecture ensures modularity (new models can be added by writing a new interface module), and the lightweight design makes daily execution feasible. By periodically feeding a fixed set of probe queries to each model and evaluating the responses, we can quantitatively track drift in performance
rohan-paul.com
. Next, we detail the types of prompts used for probing each capability dimension.

Benchmark Prompt Suite by Capability Domain

We curate a catalog of benchmark prompts covering each target dimension of “intellect.” For each capability area, a set of tailored prompts (including some edge-case and adversarial variants) will be used. The prompt suite should be diverse but small enough to run quickly each day. Below we outline the domains and example prompt types:

Logical Reasoning

This domain tests the model’s ability to perform deductive, inductive, and commonsense reasoning in both symbolic and natural language forms. Example prompts include:

Symbolic logic puzzles: e.g. syllogisms or conditional reasoning. Example: “If all X are Y and no Y are Z, can any Z be X? Explain your answer.” (Expected: a logically consistent yes/no with reasoning.)

Math word problems: multi-step arithmetic or algebra problems that require reasoning through steps (without external tools). Example: “John had 15 apples, gave away 7, then bought 12 more. How many does he have now?” (Check if the answer is correct and shows the reasoning process.)

Commonsense reasoning scenarios: e.g. “Ali is taller than Bea, Bea is taller than Cara. Who is the tallest?” or trick questions that test consistency and avoidance of obvious traps.

Evaluation: Logical reasoning prompts often have a known correct answer or solution path, enabling automatic checking. We score these by correctness of the final answer and sometimes the coherence of the explanation. For multi-step problems, partial credit can be given if the approach is right but arithmetic is wrong, etc. A consistent drop in logic puzzle accuracy or an increase in mistakes would indicate a regression in reasoning ability.

Code Synthesis & Debugging

These prompts assess coding abilities, including writing correct code, fixing bugs, and handling edge-case behavior in programs. Example tasks:

Function implementation: Provide a spec and ask the model to write code. Example: “Write a Python function that checks if a number is prime.” We then test the returned code against a set of test cases (including edge cases like 0, 1, negative, large primes).

Debugging exercise: Give the model a short snippet with a known bug and ask for a corrected version or identification of the bug. Example: Provide a function that is supposed to reverse a string but has an off-by-one error, and ask the model to fix it. The expected output is a corrected code snippet.

Edge-case coding scenarios: e.g. ask for code in an esoteric language or unusual requirement to see if the model copes (within reason). Or ask for code with specific constraints (like no built-in functions).

Evaluation: We automatically compile/run the code in a sandbox or use static analysis. Scoring is by functional correctness (did the code run and produce expected outputs for test inputs?) and completeness. For debugging, we check if the identified fix actually resolves the issue. We can track metrics like percentage of test cases passed or use known benchmarks (e.g., HumanEval for code) on a smaller scale. Over time, a decline in passed tests or an increase in errors (e.g. model starts producing partial code with “...” where it previously gave full solutions
ignorance.ai
) would be flagged.

Factual Knowledge & Domain Expertise

These prompts query the model’s knowledge base and ability to provide accurate, detailed information, especially time-sensitive facts:

Static trivia questions: Ask general knowledge questions with a single correct answer. Example: “Who was the prime minister of Japan in 2010?” (The answer is known and can be checked against references.)

Time-stamped current events: If the model or interface has access to current information (e.g. Bing or a browsing plugin), ask about recent news or events. Example: “What is the latest mission launched by NASA?” If the model has no browsing, we check how it handles the question – does it admit ignorance (knowledge cutoff) or hallucinate an answer?

Depth of expertise: Niche domain questions in science, history, etc., to see if it can provide detailed correct answers. Example: “Explain the significance of the Hopf fibration in mathematics.” We expect a reasonably correct explanation; a decline might show up as increasing errors or vagueness.

Evaluation: For factual Q&A, we compare the model’s answer to known correct answers or authoritative sources. We can use an exact-match or similarity check for simple facts, and for longer explanations, possibly have an automated verifier (another LLM or a knowledge-base lookup) confirm key facts. We log if the answer was correct, partially correct, or incorrect. Additionally, tracking citation usage (if the model provides sources) or knowledge cutoff behavior (does it correctly say “I don’t know” for post-training data) can be insightful. A “dialed down” knowledge capability might manifest as increasing errors or the model refusing to answer things it used to attempt.

Multi-step Instruction Follow-Through

Complex prompts that require following multiple instructions or performing reasoning in stages test the model’s persistence and attention throughout a task:

Composite tasks: e.g. “First, generate a list of three creative uses for a paperclip, then alphabetize that list, and finally provide a brief rhyming poem about the most interesting use.” This prompt has multiple steps in one query, checking if the model addresses all parts in order.

Interactive multi-turn tasks: In a conversational setting, give an instruction in one turn, then additional instructions or corrections in follow-up turns. Example: Turn1: “Summarize the following article [text] in one paragraph.” Turn2: “Now extract three specific statistical facts from that summary.” We check if the model can carry context from the first request to the second and not lose information.

Logical multi-step reasoning: Present a problem where the model must go through a chain of reasoning (possibly encouraged via a “think step-by-step” prompt). We then see if it reaches a correct conclusion by following the steps.

Evaluation: The output is checked for completeness and order. Did the model perform every requested sub-task correctly? We can parse the output structure to ensure, for instance, that the final response contains all required parts (the list and the poem in the first example). If the model skips or misorders steps, that’s a failure for this prompt. We score each sub-instruction as fulfilled/unfulfilled to get a follow-through score. Over time, if a model starts dropping steps or giving more incomplete answers to multi-part instructions, that indicates a degradation in following through complex prompts.

Stylistic Fluency & Consistency

These prompts assess the model’s ability to write with a specific style, tone, or persona consistently, and to maintain output quality in longer compositions:

Style mimicry: Instruct the model to produce text in a distinct style or voice. Example: “Write a paragraph about the ocean in the style of Shakespeare.” The expectation is fluent iambic pentameter and archaic diction.

Tone consistency: Maintain a persona or tone over a multi-turn dialogue or a long narrative. Example: The system might say: “You are a wise old philosopher. Answer questions with proverbs.” Then we ask it a few questions to see if it stays in character and tone throughout.

Format and coherence tests: Ask for outputs with specific format (like a limerick, a JSON snippet, or a formal letter) to see if the style constraints are followed exactly and the output remains coherent from start to finish.

Evaluation: Scoring style is more subjective, but we can automate parts of it. For format or rhyme schemes, we can programmatically check compliance (e.g., does the limerick have 5 lines with the correct rhyme pattern). For tone consistency, we might use a simple text classifier or heuristic (e.g., count archaic words for Shakespeare style) to ensure the style markers are present. Another approach is using LLM-as-a-judge: for example, prompt a separate evaluator model with “On a scale of 1-10, how well does the above text imitate Shakespeare’s style?” to get a score
medium.com
. We will log such style fidelity scores over time. A decline might show up as style imitations becoming bland or the model needing reminders to maintain persona (suggesting the model’s creative style outputs were toned down).

Memory & Context Handling

Here we test how well the model can remember and utilize earlier context in a conversation or within a long prompt, assuming the model/platform supports extended context or chat history:

Long-context recall: Provide a piece of information or a story in an earlier turn or earlier in a long prompt, then later ask a question that requires recalling that information. Example: Prompt: “Alice, Bob, and Carol attended a meeting. Alice brought coffee, Bob brought donuts, Carol brought nothing.” Later query: “Who brought donuts to the meeting?” The model should answer “Bob.”

Conversation consistency: Carry a fact or a decision through a dialog. For instance, set up: “We will refer to X as Y from now on.” Then later: “What did I ask you to call X?” expecting the model to remember the alias.

Context limit tests: If the model has a known context window (say 4K or 8K tokens), we can push near that limit by inserting filler text or multiple Q&A turns, then see if it still recalls something from the beginning.

Evaluation: This is evaluated by correctness of reference. Did the model’s answer correctly use the earlier provided context (e.g., answered “Bob” in the example, not mix up with someone else)? We simply mark success/failure based on that comparison. We may also track if the model’s responses start to contain contradictions or re-ask for info that was given (signs of context failure). Over time, if memory performance drops (e.g., the model more often forgets earlier details or gets them wrong), that’s a red flag. However, note that if a platform changes its context length (e.g., offers a longer window or resets more often), we’d need to adjust this test accordingly.

Creativity & Analogical Reasoning

To gauge creative thinking and the ability to synthesize unexpected connections, we include open-ended prompts that have no single “correct” answer but allow us to observe the model’s imaginative capabilities:

Analogy and metaphor generation: Example: “Create an analogy to explain blockchain using a kitchen scenario.” We expect a creative comparison (e.g., “miners are chefs following a shared recipe book…”). We can qualitatively judge the novelty and aptness of the analogy.

Concept blending challenges: Ask for an invention or story blending unrelated concepts. Example: “Describe a new sport that combines chess and surfing.” This tests the model’s ability to step beyond common combinations and produce a coherent, inventive idea.

Creative problem solving: Pose an open problem that requires thinking outside the box. Example: “If humans could communicate telepathically, how might architecture change? Provide a speculative analysis.” There’s no right answer, but we expect a logical yet creative exploration.

Evaluation: Creativity is the hardest to score automatically. We will rely on proxies: diversity metrics (does the model use original content or just a cliche?), length and richness of the response, and possibly an evaluator LLM to judge originality. For instance, we might prompt an evaluator with “Rate how original and imaginative the above answer is on a 1-5 scale.” Additionally, we can measure self-repetition or safe defaults – if over time the model’s creative answers become shorter or more similar to each other, creativity may be declining. This dimension likely needs manual review or periodic spot-checking to supplement automated scores. Any noticeable drop (e.g., the model starts giving very formulaic responses to these creative prompts) would be noted as a capability regression.

Incorporating Edge Cases & Adversarial Prompts: Throughout the above domains, we include some edge-case variations to stress-test the models
medium.com
. This means occasionally adding typos, slang, or ambiguous phrasing in a prompt to see if the model still handles it gracefully
medium.com
. We might also include adversarial instructions that have trapped models in the past, such as tricky arithmetic phrased oddly, or code that exploits known model weaknesses (for example, asking for a specific tricky regex that some models consistently get wrong). The suite deliberately covers a spectrum from straightforward questions to adversarial challenges. This ensures we can detect if models become more brittle on edge cases. A well-performing model might initially handle a twisted question, but if over time it starts failing that, it’s a sign of potential regression. We maintain the same adversarial prompts day to day for consistency, but can rotate in new ones if needed (with proper version tracking of the prompt set whenever we change it).

Automated Scoring Rubrics and Change Detection

To evaluate model responses objectively, we design a scoring rubric for each prompt type, enabling automatic or semi-automatic grading. The table below summarizes the scoring approach by capability domain:

Dimension	Sample Evaluation Criteria
Logical Reasoning	Accuracy of final answer (e.g. correct/incorrect for puzzles). If structured explanation is expected, check for logical consistency in the reasoning steps. Scoring: 1 if correct reasoning & answer, 0 if incorrect (partial credit for correct method with minor mistake).
Code Generation & Debugging	Functional correctness (does the code run and produce expected output?). Count of test cases passed. Error handling: Did it handle edge inputs without crashing? Score by % tests passed or binary success/fail for each task.
Factual Knowledge	Correctness of facts (compare answer to ground truth). Use exact match or semantic similarity for factual Qs. Score 1 for correct, 0 for incorrect, or partial for incomplete answer. Also track if model defers (“I don’t know”) appropriately for unknown current events.
Multi-step Follow-Through	Completeness: Did the response follow all instructions? e.g., if 3 tasks were requested, did it address each? Score could be number of sub-tasks correctly completed (e.g., 3/3). Order: Deduct if steps are out of order or combined incorrectly.
Stylistic Consistency	Style adherence: Check output against requested style constraints (format, tone, persona). Automatic checks (e.g., rhyme scheme, JSON validity) and/or LLM judge for style match
medium.com
. Rate on a scale (e.g., 0-10) how well it matches the style consistently throughout.
Memory & Context	Contextual accuracy: Did the model recall given info correctly later on? This is usually binary (success = referenced correctly, failure = forgot or erred). Track the % of memory prompts answered correctly.
Creativity & Synthesis	Originality: Use an evaluator model or heuristic to score creativity (e.g., unusualness of the answer, richness of detail). Could use a 1-5 or 1-10 creativity score. Also monitor length (a very short, dull response might indicate low effort). This remains partly manual – e.g., flag if an answer looks too generic or identical to a prior day’s answer (which could indicate the model is stuck in a rut).

In practice, each prompt’s evaluation script will output a score or categorical result. For example, a logic puzzle prompt might output correct=True, a code prompt might output passed_tests=5/5, a style prompt might output style_score=8/10, etc. These results are logged per model per day.

Aggregating and Detecting Changes: Once we have scores, the system computes aggregate metrics for each capability per model (e.g., overall accuracy % for logic prompts, average creativity score, etc.). These can be plotted over time. We define thresholds for alerting: for instance, if a score drops more than a certain percentage compared to the last week’s average, flag it. Industry practice often involves setting such thresholds – teams might run nightly tests on a standard suite and trigger investigation if metrics fall beyond a tolerance
rohan-paul.com
. Our system similarly will watch for statistically significant drops. Given the small daily sample, a persistent downward trend or a large single-day drop beyond normal variance would be highlighted.

For qualitative changes that are hard to score (e.g. style or creativity), the system can log the full outputs for manual review. By using LLM-as-a-judge techniques for intermediate scoring, we attempt to automate detection of subtle regressions (like coherence or style weakening)
medium.com
. Moreover, comparing the text outputs themselves via diffs can be revealing: if the exact same prompt yields a markedly different answer structure than before, that indicates a possible model update. All textual diffs and score changes will be included in the daily report.

Platforms to Probe and Access Methods

Not all AI platforms offer easy API access, but our system is designed to cover both public web interfaces and APIs:

OpenAI ChatGPT (GPT-3.5, GPT-4): Access: Use OpenAI’s API for GPT-4 and GPT-3.5 models. This provides programmatic access with controllable parameters. In addition, one could test the ChatGPT web UI (which might have differences in system prompts or features like browsing). If needed, a scripted browser session can log into the ChatGPT interface and input prompts. However, since the API and web UI should use the same underlying models (aside from added UI features), the API route suffices for most capabilities. We will ensure to specify model versions if possible (e.g., "gpt-4" vs "gpt-3.5-turbo"), and note any version info returned in API responses for tracking.

Anthropic Claude (Claude 2, Claude Instant, etc.): Access: Use Anthropic’s official API for Claude, providing the prompt and retrieving the completion. If the API is not available or if we want to test the freely accessible Claude (e.g., via a Slack integration or Quora’s Poe), the system can interface through those channels. For example, Anthropic has a known format for their API (prompt and parameters similar to OpenAI’s). We will include appropriate context limits (Claude supports large context windows which we might leverage in memory tests).

xAI Grok: Grok is a newer platform primarily accessed through a web interface (via X (Twitter) for authorized users). As of now, no public API is known. To probe Grok, we may employ web automation – e.g., using a headless browser to log into X and interact with the Grok chatbot. This requires careful rate limiting and possibly using official web client calls if available. Realistically, Grok’s accessibility might be limited; if it’s not feasible to automate safely, we might omit or manually run Grok probes until an API emerges. In the design, we include a module stub for Grok so it can be integrated when possible.

Other Models (Bard, Bing, etc.): Google’s Bard could be included (as a public web chatbot with no official API, though unofficial APIs exist). Similarly, Bing Chat (which runs a version of GPT-4 with web access) could be probed via the Bing web interface or using the Edge browser’s developer API. These would be optional extensions – our architecture can accommodate them via additional interface modules. If included, we’d have to ensure compliance with their terms (for instance, Bing might detect and block automated usage).

Open-Source Models for Baseline: It may be useful to include a static reference model (like a local LLaMA-2 or other model that we run ourselves and which does not change unless we update it). This can serve as a control – since it will not be “dialed up or down” by an external provider, any changes in its performance would come only from changes in the test suite or evaluation, not from the model drifting. If we see fluctuations even in the static model, that indicates an issue in our methodology. Thus, including a stable model’s daily results helps calibrate what normal random variance looks like.

For each platform, we note any constraints: e.g., rate limits (OpenAI might limit requests per minute, but our volume is low), potential costs (API calls will incur usage fees – we’ll manage by keeping prompt count modest), and difference in capabilities (some models may not support huge context or certain prompt types – we tailor the prompt suite accordingly per model, or mark N/A if a prompt doesn’t apply).

Ensuring Fair Comparison: While we probe multiple models, the goal is to track each model against its own history more than against each other (since each has different strengths). So, the prompt suite is largely model-agnostic, but we do allow some customization per model if needed (for example, a coding prompt might be skipped on a model that cannot code at all, or a very large context memory test might be adjusted if one model’s max context is much smaller than another’s). Consistency per model is key. We also consistently use the same format and instructions each day – this means storing the exact prompt text and parameters for reuse. That way, if a provider updates their model or policies, differences in output are attributable to them and not to any unintentional changes on our side.

Version Tracking, Repeatability and Trend Analysis

A core principle of this system is repeatability: using fixed probes and conditions to make comparisons valid over time. We incorporate several mechanisms for version tracking and trend analysis:

Model Version Logging: Whenever a platform provides an identifiable model version or update info, we log it. For OpenAI, this might be the model snapshot ID (e.g., GPT-4-1115 vs GPT-4-0613) if available. For others like Claude, new major versions are typically announced (Claude 1.3 vs 1.4, etc.), and we can tag runs with the known version. If the platform doesn’t explicitly give a version, we rely on date as implicit version. Maintaining this metadata allows us to correlate changes in performance with version changes (e.g., “capability X dropped after model version Y was deployed on date Z”).

Controlled Parameters: As noted, we use the same temperature, top_p, etc., to reduce randomness
github.com
. For instance, temperature=0 (greedy deterministic output) is used for tasks where we want consistency (logic, factual, code). For creativity tests, we might use a slightly higher temperature to allow variability but then the scoring focuses on quality, not exact matching. Even there, we keep the sampling settings constant each day. This acts as a repeatability control, ensuring any systematic change in outputs likely comes from model alterations, not different sampling.

Baseline and Calibration: The first week of running can establish a baseline mean and variance for each metric per model. We expect some day-to-day variance due to inherent model randomness or external factors (especially for UI-based tests). Knowing the typical variance allows setting control limits so we don’t overreact to tiny fluctuations. For example, if GPT-4’s logic puzzle accuracy oscillates between 90-95% normally, we set a threshold maybe at <85% before we flag a regression.

Historical Data Storage: All daily results are appended to a time-series log. We might use a simple CSV with columns (date, model, prompt_id, score, etc.) or a more robust database if scaling up. This data is the basis for trend analysis. We can generate graphs of each metric over time (as done in DailyBench’s public dashboard
github.com
). Trends like a gradual decline or an abrupt drop/spike become visually apparent.

Automated Diffing: Besides numeric scores, we store the raw output text (possibly truncated if very long, or at least a checksum of it). By comparing the raw outputs between dates, we can catch qualitative changes: e.g., if a model suddenly starts responding with a different style or format (perhaps due to a hidden system prompt change). A simple diff tool can highlight if, say, the model’s answer phrasing has shifted. For instance, maybe a factual answer previously included citations and now it doesn’t – the diff would show removed “[1]”-style citations. This can be a clue of underlying changes.

Trend Analytics & Reporting: The system will automatically compute week-over-week and month-over-month changes for each metric. We could incorporate statistical tests for drift (e.g., a control chart or a hypothesis test if enough data points exist) to distinguish real changes from noise. Alerts can be generated if any metric’s trend crosses a predefined threshold. For example, “GPT-4’s code test pass rate dropped by 20% compared to last week – potential regression.” The daily (or weekly) report will summarize such findings, along with charts or tables.

Over the long term, this process creates a versioned record of model behavior. If an update occurs, we can pinpoint when a change happened and in what areas. If needed, the system can be extended to run A/B comparisons (for example, if OpenAI allows querying an old version and a new version side by side, we could integrate that to directly compare responses). In general, by maintaining consistency and logging richly, we uphold the principle: if today’s score is much lower than last week’s on the same test, something has degraded
rohan-paul.com
 – and our system will catch it.

Stress-Testing with Creative and Adversarial Techniques

To robustly test for “dialing down” of capabilities, the system employs creative and adversarial stress tests beyond the normal usage scenarios. These are designed to reveal subtle regressions that might not show up in straightforward queries:

Adversarial Reasoning Problems: We include trick questions or problems known to fool earlier models. For example, a question with a false premise or a known paradox. Historically, a strong model might have navigated the trick correctly; if in the future it starts answering incorrectly or evasively, that suggests a change. Such queries push the logical reasoning under abnormal conditions.

Noisy or Hard-to-Parse Inputs: We purposely add some prompts with typos, jumbled syntax, or irrelevant details to see if the model’s robustness changed. A capable model should handle minor typos or extraneous info. If a model suddenly fails or refuses more often on these, it might indicate a shift (perhaps stricter input parsing or reduced tolerance for ambiguity).

Jailbreak and Policy Edge Cases: Without violating usage policies, we craft some prompts that tread close to the model’s content boundaries or request slightly unusual formats. The idea is to see if the model’s compliance or refusal behavior changes over time. For instance, a prompt: “Explain a mildly controversial historical event from both supportive and critical perspectives.” This should be allowed, but if a model becomes more cautious, it might start refusing or sanitizing the answer excessively. Noting changes in how it handles sensitive-but-allowed queries can reveal if new safety filters are effectively “dialing down” its responsiveness. We track the rates of refusals or safe-completions (when the model gives a generic safe answer) on such prompts.

Increasing Complexity: Another approach is to gradually ramp up the difficulty of a task until the model fails, and see if that threshold changes. For example, give arithmetic problems with increasing number of steps or code with increasing complexity, or increase the amount of context to recall. Initially record at what point the model starts faltering. Repeating this over time might show that threshold moving (e.g., maybe originally the model handled 5-step reasoning but later only manages 3 steps reliably). This requires more dynamic testing, but could be done periodically (not necessarily daily for all models, perhaps as a weekly deeper test).

Analogical Creativity Tests: We push creative prompts to see if the model becomes less original. For instance, a prompt like “Invent a new word and define it” – a creative model will produce a novel word with a clever definition. If over time the responses become more mundane or it reuses words, that’s a sign of reduced creativity. Similarly, “Tell a joke that combines quantum physics and slapstick comedy” – we’d observe if the humor or originality declines (e.g., it starts giving a generic joke or says it can’t).

By including these stress tests, we ensure the monitoring isn’t just covering the “happy path” queries but also the edge of the model’s capabilities. Adversarial prompts are particularly important because regressions often appear first at the extremes (a slightly weaker model might still get easy questions right but start failing the hard ones). As noted in one guide, incorporating edge and adversarial cases in evaluation helps catch issues early
medium.com
. Our system will highlight any changes in how the model handles these stressed scenarios – for example, if a model that used to deftly answer a tricky riddle now gets it wrong or refuses to attempt it, that’s a noteworthy change.

Trade-offs and Considerations

Designing this probe system involves several trade-offs and challenges:

Automatic Scoring vs Human Judgment: While we strive for automated scoring, not everything can be perfectly measured by a script. There is a trade-off between coverage and evaluation fidelity. We address this by using LLM-based graders for nuanced aspects, but that introduces an additional model (which itself could change over time). We mitigate this by using a strong, presumably more stable evaluator (or even a frozen earlier model version as the judge). Important changes might still warrant human review in the loop to confirm real regressions versus scoring noise.

Prompt Set Maintenance: Over long periods, the fixed prompt set could become either too easy (models might eventually memorize or overfit those exact questions if similar ones are in training data or via updates) or not reflective of newer concerns. We may need to update the prompt suite periodically. However, any update to prompts can itself cause a score shift unrelated to the model – so we’d version-control the prompt set and possibly run overlap (old and new) during a transition period to calibrate. This is a known challenge in long-term evaluations: ensuring the test doesn’t grow stale while maintaining comparability.

Platform Differences and Fairness: Each platform has unique characteristics (context length, default system prompts, etc.). Directly comparing scores between, say, GPT-4 and Claude might be less meaningful than tracking each one’s trend. Our focus is on relative change per model. We must be careful in any comparative analysis, controlling for differences in prompt handling. Also, using web UIs might have more variability (due to rate limiting, session context carryover, etc.) than APIs. We accepted that some variance exists
github.com
 and address it by focusing on clear trends rather than single data points.

Cost vs. Frequency: Calling multiple high-end models (GPT-4, Claude, etc.) every day on a suite of prompts has a monetary cost. We choose a minimal representative set of prompts so that the daily run is affordable (the number of API calls might be on the order of tens, not thousands). Running more frequently (like multiple times a day) can catch intra-day changes but also multiplies cost. Our design suggests daily as a balance, with optional increased frequency if needed for certain models or during suspected changes.

Data Management and Analysis Overhead: Storing daily outputs and metrics will accumulate a sizable log. We need a strategy for data retention – possibly keep detailed records for X days and aggregate older data (as DailyBench does
github.com
). Also, analyzing multi-dimensional data (7+ capability metrics across several models) could become complex. We will implement simple summary views (e.g., each model gets a “scorecard” of all dimensions) and possibly a composite score. However, a single composite metric may obscure which specific capability regressed, so we lean toward presenting the breakdown per dimension.

Alert Fatigue vs Sensitivity: We must tune the alerting threshold so that we don’t flag normal fluctuations (avoiding false alarms), yet catch real regressions in a timely manner. This might involve accumulating a few days of downturn before raising a flag, or using statistical tests to distinguish signal from noise. It’s a trade-off between sensitivity (detect every tiny change) and specificity (only report meaningful changes). We plan to refine this using the baseline data – for instance, if a metric historically varies ±5%, we set threshold beyond that range.

Ethical and Terms Considerations: Probing models via unofficial means (like web scraping a UI) could violate terms of service. We should prioritize official APIs and ensure we are not breaching usage policies. Also, continuously testing models on possibly sensitive edge cases means we must handle the outputs responsibly (e.g., if an adversarial prompt triggers an unsafe response, we need to flag that but not publish it raw). All data and prompts should be chosen with ethical guidelines in mind, avoiding truly disallowed content. The aim is to test capabilities, not to cause the model to produce harmful content.

Continuous Updates from Providers: If a model does change (for better or worse), providers might not announce it. Our system might be one of the few signals that a change occurred. We should be cautious in interpreting results – if a drop is detected, it could be intentional alignment tuning (not exactly “worsening” the model, but prioritizing safety), or a temporary issue. Our tool surfaces the facts (performance changed in X metric), but diagnosing the root cause might require deeper analysis or provider communication.

Despite these challenges, the benefits of such a monitoring system are significant: it provides transparency and early warning if an AI service’s quality shifts. In production settings, this is crucial to trust and reliability
rohan-paul.com
rohan-paul.com
. Users and developers can adapt or investigate quickly rather than relying on anecdotal reports.

Next Steps and Implementation Plan

With the design laid out, the following steps will kick-start this project:

Prototype with One Model: Implement the core pipeline (scheduler -> prompt -> API -> evaluation -> logging) for a single platform (e.g., OpenAI GPT-4) and a small subset of prompts for each dimension. This will test end-to-end functionality and allow tuning of prompts and scoring scripts on real outputs.

Expand Prompt Catalog & Models: Gradually add the full prompt suite and onboard additional models (Claude, etc.), verifying that each interface module works reliably. We’ll obtain API access or set up automation for each. We also incorporate the static baseline model (if used) at this stage.

Automate Scoring & Verification: Write the evaluation scripts for each prompt type. Where needed, integrate an evaluator LLM (possibly GPT-4 itself or another strong model) for judging open-ended answers. We will test these rubrics on sample outputs to ensure they correlate with human judgment. For example, we might manually rate a few days of creative answers to see if the automated method agrees.

Data Storage & Dashboard: Set up a simple database or even a Google Sheets/CSV logging initially. Simultaneously, start building a basic dashboard or report generator. This could be as simple as a Python script that produces an Markdown or HTML report with tables/plots of recent results. Later, we can enhance it with interactive charts (leveraging libraries or even publishing to a small web dashboard like DailyBench does
github.com
).

Establish Baseline & Thresholds: Run the system for a few weeks to gather baseline metrics for each model. During this phase, adjust any prompt or scoring issues (if a prompt turns out too ambiguous, refine it; if an automatic score is too noisy, tweak the method). Once metrics stabilize, calculate the normal range and set preliminary thresholds for alerts (e.g., 95% confidence intervals or a fixed % drop).

Incorporate Version Control & Diffing: Integrate version info retrieval for each model (for APIs that provide it). Also implement text diffing on outputs and a mechanism to highlight differences in the report. For example, if today’s output for Prompt A differs, show a snippet of yesterday vs today in the report.

Trial Run of Adversarial Cases: Particularly monitor the adversarial prompts during the baseline period to ensure they’re not causing erratic behavior (e.g., if a prompt is so tricky that even a stable model fails randomly half the time, it may be too noisy as a daily probe – we might replace it with a slightly easier but still challenging one). The goal is to have reliable canaries – tasks that a healthy model usually can do, and only a degraded model would fail.

Deploy Scheduling & Notifications: Once stable, deploy the scheduler on a server or CI pipeline. For example, schedule a daily GitHub Action or a cron job on an EC2/VM. Implement email or Slack notifications for when a significant change is detected (could be as simple as “if any alert flag is true, send message with summary”).

Ongoing Maintenance: Continuously monitor the monitors, so to speak. If the system flags a regression, verify it (possibly by re-running the prompts manually to rule out any glitch). If confirmed, the next step might be to reach out to the provider or adjust usage. Also update the prompt suite over time to keep it relevant (with careful version tracking as noted).

By following these steps, we will have a robust continuous evaluation harness for AI models. This system will act as an early-warning radar for capability changes. It draws on best practices from software regression testing and emerging MLOps monitoring approaches, applied in the context of AI model services
rohan-paul.com
rohan-paul.com
. Ultimately, the insights gained can inform users about model reliability (e.g., “Claude’s coding skills have been steady, but its factual accuracy dipped this month”) and push model providers toward greater transparency about updates.

Conclusion: This decision brief presented an architecture and plan to daily probe and track AI model performance across a spectrum of intellectual tasks. By logging and analyzing results over time, the program can detect if models are secretly “nerfed” or otherwise changed. The design balances thoroughness with efficiency, covering logical reasoning, coding, knowledge, multistep following, style, memory, and creativity in a modular test suite. With scoring rubrics and trend analysis in place, the system will provide actionable data on model drift. The next step is to implement a prototype and iteratively refine it. In an era of rapid AI evolution, having an independent gauge of model capability is crucial to maintain trust and performance for end-users. This system aims to be that gauge – continuously measuring the pulse of our AI models, and catching the moment it skips a beat.

Sources: The approach and considerations above draw upon existing research and practices in LLM evaluation and monitoring, including continuous benchmark initiatives
github.com
rohan-paul.com
, recommendations for incorporating adversarial test cases
medium.com
, and recent observations of model performance drift
ignorance.ai
. These sources underscore the importance of systematic, ongoing evaluation in detecting performance regressions in AI models.
