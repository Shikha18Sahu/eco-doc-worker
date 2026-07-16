# Audit & Logging Documentation

## What Gets Logged

Every agent appends a `HistoryEntry` to `WorkflowState.history` every time it runs:

| Field | Description |
|---|---|
| `timestamp` | UTC timestamp of this step |
| `agent` | Which agent ran |
| `input_summary` | Short description of what the agent received |
| `output_summary` | Short description of what the agent produced/decided |
| `decision` | Optional — e.g. `"pass"`, `"fail"`, `"approve"`, `"escalate"` |
| `confidence` | Optional — confidence value at this step, if applicable |
| `duration_ms` | How long this agent took |
| `error` | Optional — any error message caught during this step |

## Where Logs Are Stored

1. **Per-workflow JSON file** — `data/logs/{workflow_id}.json`, written by `LoggerAgent`, containing the entire final `WorkflowState` (including full `history`).
2. **SQLite** — `data/workflow.db`, a `workflows` table with one row per workflow: key fields (status, confidence, document type) as queryable columns, plus the full state as a JSON blob (`state_json`) for complete reconstruction.

## Why Both

JSON logs are immutable, human-readable, and easy to diff/inspect per document. SQLite enables fast programmatic lookup (`GET /api/workflow/{workflow_id}`) without needing to know a file path. Neither replaces the other — this is intentional duplication for two different consumption patterns (audit review vs. application queries).

## What Is NOT Currently Logged

- Raw uploaded image retention policy (images persist indefinitely in `data/uploads/` — no cleanup job yet)
- Structured, queryable per-agent metrics across workflows (e.g. "average OCR confidence this week") — currently would require manually querying/aggregating the JSON logs or SQLite rows.