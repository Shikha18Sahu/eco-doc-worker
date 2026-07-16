# ARCHITECTURE

## High-Level Diagram

Frontend (React) sends an HTTP request to FastAPI. FastAPI hands the
request to the Harness, which governs execution of the LangGraph
pipeline below:

Image Quality -> OCR (retry once) -> Classification -> Schema Lookup ->
Extraction -> Validation -> Confidence -> Decision -> Logger

The Logger writes to SQLite and to per-workflow JSON audit logs.

## Why Schema-Driven Extensibility

The system supports 4 document types today (resume, employee
onboarding, student admission, KYC), each defined by a JSON file in
`app/schemas/`. Adding a 5th type requires **only adding a new JSON
file** — no changes to `ClassificationAgent`, `ExtractionAgent`,
`ValidationAgent`, `DecisionAgent`, or `workflow_graph.py`.

This works because:
- `SchemaLoader` discovers schemas dynamically by scanning the folder
- `ClassificationAgent` gets its list of "known types" from
  `SchemaLoader.list_known_types()` — never hardcoded
- `ExtractionAgent` and `ValidationAgent` read `required_fields`,
  `optional_fields`, and `validation_rules` from whatever schema
  matched — never a fixed field list in Python

## Handling the Unknown Case

If `ClassificationAgent` cannot match a document to any known schema,
it returns `"unknown"`. Every downstream agent checks whether a schema
was found, and treats a missing schema as a graceful stop, not an
error — culminating in `DecisionAgent` returning the explicit message:
"Unknown document type. No validation schema available. Escalating
for human review."

## Schema Shape (Designed for Future Extensibility)

Each schema JSON file follows this shape:

- `document_type` — string identifier, e.g. "resume"
- `description` — human-readable description
- `required_fields` — list of field names that must be present
- `optional_fields` — list of field names that may be present
- `validation_rules` — a dictionary keyed by field name, where each
  value is itself a dictionary describing that field's expected type
  (e.g. `email`, `phone`, `date`, `number`, `string`)

Because `validation_rules` is a dictionary keyed by field name, future
rule types such as `regex`, `min_length`, or `enum` can be added as
extra keys per field later, without restructuring any existing schema
file.

## Retry & Circuit Breaker Flow

OCR runs and produces a confidence score. If that confidence is below
0.6, the OCR node calls `CircuitBreaker.register_retry()`. This
increments the retry counter and checks it against `max_retries`
(which is 1). If the counter is still within the limit, the graph
loops back to OCR once more. If the limit has been exceeded, the
Circuit Breaker forces an escalation instead of allowing another loop
— this is what prevents infinite retry cycles.

## Why LangGraph + Harness Together

LangGraph alone defines *reachable paths* through the workflow. It does
not, by itself, enforce cross-cutting rules like "never retry more
than once" or "never trust an agent's output without verifying its
shape." The Harness layer (see `CLAW.md`) adds this governance without
requiring every agent to reimplement it.