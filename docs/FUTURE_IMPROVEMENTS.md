# Future Improvements

## OCR Quality
- Add image preprocessing (contrast enhancement, deskewing, upscaling) before EasyOCR to improve accuracy on dense/small-font documents.
- Evaluate TrOCR (transformer-based OCR) specifically for handwritten documents, where EasyOCR's accuracy was observed to be low during testing (~11% confidence on a handwriting-heavy sample).
- Consider a cloud OCR fallback (Google Vision, AWS Textract) for cases where local OCR confidence is persistently low across retries.

## Validation Rules
- Implement the `type` values already defined in schema `validation_rules` (email, phone, date, number, string) as actual format checks — currently the schema declares these but the ValidationAgent only checks presence, not format.
- Add support for `regex`, `min_length`, `max_length`, and `enum` keys per field, as the schema shape was explicitly designed to support without restructuring.

## Document Types
- Add more schema files as new business needs arise — no code changes required, per the extensibility design.
- Consider per-schema confidence thresholds (some document types may warrant stricter approval bars than others) instead of one global threshold.

## Data Retention
- Add a cleanup/retention policy for `data/uploads/` — currently uploaded images persist indefinitely.
- Add configurable log retention/archival for `data/logs/`.

## Harness
- Replace `HealthChecker`'s stubbed checks with real pings to the OCR engine and Gemini API before each run.
- Add a proper `OutputVerifier` check for `ClassificationAgent`'s output, matching the pattern already used for `ExtractionAgent`.

## Frontend
- Add a "human review queue" view for escalated workflows, allowing a reviewer to manually correct fields and re-submit.
- Add document-type selection/preview before upload, rather than relying solely on auto-classification.

## Observability
- Add structured, cross-workflow metrics (e.g. average confidence per document type per week) — currently would require manual aggregation across JSON logs/SQLite rows.

## Deployment
- Add authentication to the API before any real deployment (currently open, appropriate only for local/internal demo use).
- Add environment-specific configs (dev/staging/prod) rather than a single `.env`.