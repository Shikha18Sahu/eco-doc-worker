# Escalation Policy

## Conditions That Trigger Escalation

1. **Unknown document type** — classification didn't match any registered schema. Always escalates immediately, regardless of confidence.
2. **Validation errors + low confidence** (`confidence < 0.5`) — missing required fields combined with low trust in the OCR/extraction result.
3. **No validation errors, but confidence below approval threshold** (`confidence < 0.75`) — the extraction looks complete, but confidence isn't high enough to auto-approve, and there are no missing fields to specifically ask the user about, so it goes to a human.
4. **OCR retry limit exceeded** — after one failed retry, confidence is still low; the circuit breaker forces escalation rather than looping again.
5. **Image quality failure** — image too blurry or below minimum resolution; flagged for human review before OCR is even trusted.

## Conditions That Trigger "Ask User" (not full escalation)


Validation errors present, but confidence is still reasonably high (`>= 0.5`) — the system believes the extraction is mostly trustworthy, just missing specific fields it can name, so the appropriate action is asking the user to supply those specific fields rather than routing to a human reviewer for a full re-check.
When a workflow is in this state, the frontend displays input fields
for exactly the missing field(s), and the user can submit them via
`POST /api/workflow/{workflow_id}/resume`. This re-runs validation,
confidence, and decision — without repeating OCR or extraction — so a
single missing field doesn't require re-uploading the entire document.

## Conditions That Trigger Approval

No validation errors AND confidence >= 0.75.

## Design Rationale

Thresholds (`0.5`, `0.75`, `0.6` for OCR retry) are deliberately simple, human-tunable constants (`app/agents/decision_agent.py`, `app/agents/ocr_agent.py`) rather than hidden in code logic — a reviewer or engineer can look at one place and understand exactly when the system escalates.