# Savvital Assessment

## How to Run

### Prerequisites

```bash
pip install uv        # if not already installed
uv sync               # installs all dependencies from pyproject.toml
```

---

### Task 1 — AI Intake Triage

1. create`.env` in the root directory and paste your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
   Or switch to local Ollama by setting `PROVIDER = "ollama"` in `task1_intake_triage/config.py`.

2. Run the triage from the root directory:
   ```bash
   uv run python -m task1_intake_triage.intake_triage
   ```

3. Outputs written to `task1_intake_triage/`:
   - `sample_output.json` — structured recommendations for each client
   - `evidence_log.docx` — full prompt + LLM response log per profile

**To view without running:** open `task1_intake_triage/sample_output.json` and `evidence_log.docx` directly.

---


## Task 1 — Prompt Design & Production Notes

### Prompt Design Choices

The prompt is built around two ideas: role-setting and strict output control. The system message casts the LLM as a "senior estate planning attorney AI" so the model draws on the right vocabulary and reasoning style rather than answering generically. The user prompt then structures the client profile as labelled bullet points — age, marital status, children, property, business — rather than a free-text paragraph, because structured input produces more consistent structured output. Urgency rules and example mappings are spelled out explicitly at the bottom of the prompt (`Age 55+ → High`, `young single no assets → Low`) so the model does not have to infer thresholds itself. Output is constrained to four allowed instruments via a Pydantic schema enforced through LangChain's `with_structured_output`, which means any hallucinated instrument causes a validation error and triggers a retry with targeted error feedback rather than silently passing bad data downstream.

### One Thing to Change for Production

Replace the flat `clients.json` intake file with a proper queue — a database table or a message broker topic (e.g. Postgres + a simple worker, or SQS). The current file-based approach processes all clients in one batch and has no way to handle partial failures, re-queue a single failed profile, or accept new clients while the job is running. A queue gives you retry semantics, idempotency, and the ability to scale workers horizontally without any code changes.

### How to Add a Human-Review Step

After `call_llm_with_retry` returns a result inside `run_triage`, add a confidence gate before writing to `sample_output.json`:

```python
parsed = result.model_dump()

if parsed["urgency_flag"] == "High":
    parsed["status"] = "pending_review"
    review_queue.append(parsed)   # write to pending_review.json
else:
    parsed["status"] = "auto_approved"
    all_results.append(parsed)
```

High-urgency cases get written to a `pending_review.json` (or a database table with `status = 'pending'`). A reviewer reads that file, approves or edits, and a second script promotes approved records into the final output. Low and Medium cases pass through automatically. This keeps the human in the loop only where the stakes are highest, without blocking the whole pipeline.

---
