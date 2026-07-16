# Workflow Documentation

## Pipeline Stages (in order)

1. **Image Quality Check** — rejects images that are too blurry (Laplacian variance) or below minimum resolution, before wasting an OCR call on unusable input.
2. **OCR** — EasyOCR extracts raw text and an average confidence score. Retried once if confidence < 0.6 (see `RETRY_STRATEGY.md`).
3. **Classification** — Gemini classifies the OCR text into one of the registered schema types, or `"unknown"` if no match.
4. **Schema Lookup** — `SchemaLoader` retrieves the matching JSON schema (required fields, optional fields, validation rules) for the classified type.
5. **Extraction** — Gemini extracts exactly the fields defined by the matched schema — never more, never invented.
6. **Validation** — checks extracted fields against the schema's `required_fields`; missing ones become `validation_errors`.
7. **Confidence Scoring** — combines OCR confidence with a penalty per validation error.
8. **Decision** — Approve / Retry OCR / Ask User / Escalate, based on confidence + validation state (see `ESCALATION_POLICY.md`).
9. **Logging** — persists the full state to a JSON audit file and a SQLite row.

## Conditional Branches

- **OCR retry loop:** stage 2 can loop back to itself once if confidence is low, governed by the Harness's circuit breaker.
- **Unknown document type:** if stage 3 returns `"unknown"`, stages 4–7 short-circuit (no guessing), and stage 8 escalates with an explicit message.
- **Ask-user resume path:** if the Decision stage returns `ask_user`,
  the user can supply missing fields via a separate lightweight graph
  (`continue_workflow_graph.py`) that only re-runs validation,
  confidence, and decision — not the full pipeline.

## What Never Changes When Adding a New Document Type

Stages 1, 2, 3, 6, 7, 8, 9 and the graph wiring in `workflow_graph.py` are all document-type-agnostic. Only a new JSON file in `app/schemas/` is needed to add a 5th document type — see `ARCHITECTURE.md`.