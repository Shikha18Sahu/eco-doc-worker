# STATE — WorkflowState

## Why a Single State Object

Every agent, the Harness, and the LangGraph node functions all read
from and write to one `WorkflowState` object. This avoids scattered
variables and dict-key typos, and gives the whole system one place to
reason about "what does a workflow look like right now."

## Fields

| Field | Purpose |
|---|---|
| `workflow_id` | Unique ID for this workflow run |
| `document_id` | Unique ID for the uploaded document |
| `status` | Current `WorkflowStatus` enum value |
| `current_step` | Human-readable current step name |
| `retry_count` / `max_retries` | Enforces the OCR retry limit |
| `raw_ocr_text` | Raw text from OCR |
| `structured_data` | Extracted fields (plus internal `_`-prefixed keys like `_document_type`, `_image_path`) |
| `confidence` | Final confidence score after OCR + validation penalties |
| `validation_errors` | List of human-readable validation failure messages |
| `next_action` | The `NextAction` enum decided by the Decision Agent |
| `human_review_required` | Boolean flag for escalation cases |
| `history` | List of `HistoryEntry` — the full audit trail |
| `created_at` / `updated_at` | Timestamps |

## Why Enums, Not Strings

`WorkflowStatus` and `NextAction` are Python `Enum` classes, not free
strings. This means a typo like `"aproved"` is rejected immediately by
Pydantic at assignment time, rather than silently passing through and
causing a bug three steps later.

## The `_`-Prefixed Internal Keys Convention

`structured_data` holds both business fields (name, email, etc.) and
internal pipeline metadata (`_image_path`, `_document_type`). The
underscore prefix is a convention — not enforced by Pydantic — used to
distinguish "data extracted from the document" from "data the pipeline
needs to pass between agents." API responses strip these before
returning to the client.

## How State Flows
Image Quality → OCR → Classification → Extraction → Validation →
Confidence → Decision → Logger

Every node function in `app/graph/workflow_graph.py` takes the current
`WorkflowState`, passes it to an agent's `.run()`, and returns the
(mutated) state — LangGraph then merges this into the graph's overall
state for the next node.