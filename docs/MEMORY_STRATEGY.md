# Memory Strategy

## Short-Term Memory (within a single workflow run)

The `WorkflowState` Pydantic object is the short-term memory. It's created fresh per upload, passed through every LangGraph node, mutated in place by each agent, and discarded from memory once the HTTP response is returned — it does not persist in RAM between requests.

The `history: list[HistoryEntry]` field inside `WorkflowState` is the in-run memory of "what happened so far" — every agent reads prior entries implicitly through state fields (e.g. `retry_count`, `confidence`) rather than re-reading raw history text, keeping agent logic simple and deterministic.

## Long-Term Memory (across workflow runs)

Two persistence layers, serving different purposes:

1. **JSON audit logs** (`data/logs/{workflow_id}.json`) — one file per workflow, human-readable, immutable once written. Used for audit/compliance review of a specific document's journey.
2. **SQLite** (`data/workflow.db`) — one row per workflow with key fields extracted for fast querying (status, confidence, document type) plus the full state as a JSON blob. Used for programmatic lookup via `GET /api/workflow/{workflow_id}`.

## What Is NOT Persisted

Uploaded raw image files are stored under `data/uploads/` but are not automatically cleaned up — a production version would add a retention/deletion policy (see `FUTURE_IMPROVEMENTS.md`).

## Why No Cross-Workflow Memory (by design)

Each document is processed independently. The system does not "remember" previous documents from the same user/session — this is intentional: document processing correctness should not depend on hidden state from unrelated prior uploads.