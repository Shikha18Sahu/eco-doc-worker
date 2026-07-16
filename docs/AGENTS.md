# Agents

Each agent is an independent class with a strict contract: it receives
a `WorkflowState`, does one job, and returns an updated `WorkflowState`.
Agents never call each other directly — they only communicate through
state, orchestrated by the LangGraph graph.

---

## ImageQualityAgent
**Responsibility:** Verify the uploaded image is usable before OCR runs.
**Input:** `WorkflowState` (with uploaded image path)
**Output:** `WorkflowState` with quality decision recorded in history
**Decision Logic:** Currently a stub (assumes acceptable quality); designed
to later check blur, resolution, and contrast.
**Failure Handling:** On failure, appends to `validation_errors` and sets
`human_review_required = True`.

## OCRAgent
**Responsibility:** Extract raw text from the document image using EasyOCR.
**Input:** Image path (stashed in `structured_data["_image_path"]`)
**Output:** `raw_ocr_text`, `confidence` (OCR confidence)
**Decision Logic:** If OCR confidence < 0.6, sets `next_action = RETRY_OCR`.
**Failure Handling:** Retried at most once (enforced by the Harness's
CircuitBreaker, not by this agent). If retry limit is exceeded, the
graph routes to escalation instead of looping forever.

## ClassificationAgent
**Responsibility:** Classify the document into one of the known schema
types, or `"unknown"` if it matches none.
**Input:** `raw_ocr_text`, list of known types (from `SchemaLoader`)
**Output:** `structured_data["_document_type"]`
**Decision Logic:** Uses Gemini to propose a type, but the agent only
accepts the LLM's answer if it's actually in the known-types list —
otherwise it forces `"unknown"`. The agent never invents a new type.
**Failure Handling:** Any LLM/API error defaults to `"unknown"` — a
graceful degrade, not a crash.

## ExtractionAgent
**Responsibility:** Extract exactly the fields defined by the matched
document's schema (required + optional fields) — nothing more, nothing
invented.
**Input:** `raw_ocr_text`, schema's field list
**Output:** `structured_data` populated with schema fields
**Decision Logic:** If no schema was matched, extraction is skipped
entirely (no guessing).
**Failure Handling:** If the LLM's output fails schema verification,
the agent falls back to normalized raw values rather than discarding
all previously-extracted good fields.

## ValidationAgent
**Responsibility:** Check extracted fields against the schema's
`required_fields`.
**Input:** `structured_data`, matched schema
**Output:** `validation_errors` (list of missing-field messages)
**Decision Logic:** Business rules for "what's mandatory" live entirely
in the schema JSON — this agent never hardcodes field names.
**Failure Handling:** If no schema was matched, validation is skipped
(DecisionAgent handles the unknown-type case explicitly).

## ConfidenceAgent
**Responsibility:** Combine OCR confidence with validation results into
one final confidence score.
**Input:** OCR `confidence`, count of `validation_errors`
**Output:** Updated `confidence` (penalized per validation error)
**Decision Logic:** `final_confidence = max(0, base_confidence - 0.15 * num_errors)`
**Failure Handling:** N/A (pure calculation, no external calls).

## DecisionAgent
**Responsibility:** Make the final call: Approve / Retry OCR / Ask User
/ Escalate.
**Input:** `confidence`, `validation_errors`, matched schema (or lack thereof)
**Output:** `next_action`, `status`, `human_review_required`
**Decision Logic:**
- No schema matched → Escalate with explicit "Unknown document type" message
- Validation errors + confidence < 0.5 → Escalate
- Validation errors + confidence ≥ 0.5 → Ask User
- No errors + confidence ≥ 0.75 → Approve
- No errors + confidence < 0.75 → Escalate
**Failure Handling:** N/A (this agent is the failure-handling decision point for the rest of the pipeline).

## LoggerAgent
**Responsibility:** Persist the final workflow state for audit purposes.
**Input:** Full `WorkflowState`
**Output:** JSON file in `data/logs/{workflow_id}.json` + SQLite row
**Decision Logic:** None — pure persistence.
**Failure Handling:** N/A (runs last, after all decisions are made).