# API Documentation

Base URL (local): `http://127.0.0.1:8000`

## GET /health

Health check. No parameters.

**Response 200:**
```json
{ "status": "ok", "service": "eko-doc-worker-backend" }
```

## POST /api/workflow/start

Uploads a document image and runs it through the full autonomous pipeline synchronously.

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file (image) | yes | The scanned/handwritten document image |

**Response 200:**
| Field | Type | Description |
|---|---|---|
| `workflow_id` | string | Unique ID for this run |
| `status` | string | One of: `approved`, `escalated`, `awaiting_user_input`, `failed` |
| `next_action` | string | One of: `approve`, `retry_ocr`, `ask_user`, `escalate`, `none` |
| `confidence` | float | Final confidence score (0.0–1.0) |
| `structured_data` | object | Extracted fields per the matched schema (`_document_type` included) |
| `validation_errors` | array[string] | Human-readable validation failure messages |
| `human_review_required` | bool | Whether this workflow needs a human reviewer |

**Response 500:** Internal error (should be rare — the Harness is designed to convert failures into graceful `escalated` states rather than 500s wherever possible).

## POST /api/workflow/{workflow_id}/resume

Continues a workflow after the user supplies previously-missing fields.
Used when a prior `/workflow/start` response had `next_action: "ask_user"`.
Skips OCR/classification/extraction — only re-runs validation,
confidence scoring, decision, and logging.

**Request body:**
```json
{ "additional_fields": { "email": "user@example.com" } }
```

**Response 200:** Same shape as `/workflow/start`'s response.

**Response 404:** Workflow not found.

## GET /api/workflow/{workflow_id}

Fetches a previously completed workflow's full stored record from SQLite.

**Response 200:** Full SQLite row including `state_json` (the complete `WorkflowState` at completion).

**Response 404:**
```json
{ "detail": "Workflow not found" }
```

## Interactive Docs

FastAPI auto-generates Swagger UI at `/docs` and ReDoc at `/redoc` — useful for manual testing without a frontend.