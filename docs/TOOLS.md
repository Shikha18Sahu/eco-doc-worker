# Tools & External Services

## OCR Engine — EasyOCR
Wrapped by `app/services/ocr_service.py`. Loaded once (lazily) as a
module-level singleton to avoid reloading models on every request.
Returns raw text plus an average per-detection confidence score.

**Known limitation:** EasyOCR performs well on simple, single-column
forms but has reduced accuracy on dense, multi-column documents (e.g.
resumes with icons and small fonts). A production deployment would
likely swap this for a cloud OCR service (Google Vision, AWS Textract)
or TrOCR for handwriting-heavy or complex-layout documents.

## LLM — Gemini Flash
Wrapped by `app/services/llm_service.py` via the `google-generativeai`
SDK. Used for two distinct purposes:
1. **Classification** — decide which known document type (if any) the
   OCR text matches
2. **Extraction** — pull out exactly the fields defined by the matched
   schema

The LLM is never trusted blindly: classification results are checked
against the known-types list, and extraction results are checked
against a Pydantic schema before being accepted into `structured_data`.

**Model:** `models/gemini-flash-lite-latest` (chosen for being a stable,
non-preview alias with free-tier availability).

## Schema Loader
`app/services/schema_loader.py` reads all `.json` files in
`app/schemas/` at first use and caches them in memory, keyed by
`document_type`. This is the extensibility mechanism described in
`ARCHITECTURE.md` — no other code needs to change to add a new
document type.

## SQLite
Used via Python's built-in `sqlite3` module (`app/db/`). Stores one row
per workflow with key fields plus the full state as JSON, for queryable
long-term persistence.