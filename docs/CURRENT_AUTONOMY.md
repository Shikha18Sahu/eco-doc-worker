# What the Current Version Does Autonomously

This system runs the entire document-processing workflow end-to-end
without any human input, from upload to final decision, unless the
workflow itself decides human review is required.

## Fully Autonomous Steps (no human involved)

1. **Accepts** any uploaded document image via the API.
2. **Assesses image quality** (blur via Laplacian variance, minimum
   resolution) and flags issues without human input.
3. **Runs OCR** (EasyOCR) and automatically retries once if confidence
   is low — no one tells it to retry, it decides based on its own
   confidence score.
4. **Classifies** the document into one of 4 known types (resume,
   employee onboarding, student admission, KYC) or correctly
   identifies it as unknown — without a human pre-labeling it.
5. **Loads the correct schema** for that document type automatically.
6. **Extracts structured fields** defined by that schema using Gemini
   — no human specifies which fields to look for per-upload.
7. **Validates** extracted fields against the schema's required fields
   automatically.
8. **Calculates a final confidence score** combining OCR quality and
   validation results.
9. **Makes the final decision** — Approve, Retry OCR, Ask User, or
   Escalate — entirely on its own, based on fixed, inspectable rules
   (see `ESCALATION_POLICY.md`).
10. **Writes its own audit trail** — every agent's action, decision,
    and confidence — without being told to log anything per-request.

## Where the System Correctly Decides NOT to Act Autonomously

The system is designed to recognize the limits of its own confidence
and hand off to a human rather than force a decision:
- Unknown document types are never guessed into the nearest schema.
- Missing required fields are never filled in with placeholder/guessed
  values.
- Low-confidence extractions are never silently approved.

This is intentional: autonomy in this system means "run the full
pipeline and make a well-reasoned decision," not "always produce an
approval." Recognizing uncertainty and escalating it is itself part of
the autonomous behavior, not a failure of it.

## What Still Requires a Human (by design, today)

- Actually reviewing and resolving `escalated` / `awaiting_user_input`
  workflows — the system flags these but does not yet have a UI for a
  reviewer to correct and resubmit (see `FUTURE_IMPROVEMENTS.md`).
- Defining new document schemas — a developer/business owner still
  decides what fields are required for a new document type.