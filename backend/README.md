# Autonomous AI Document Processing Worker

An autonomous AI worker that owns an entire document-processing business
workflow — from image upload to a final Approve / Retry / Ask-User /
Escalate decision — rather than a single LLM call wrapped in an API.

## What this is NOT
- Not a chatbot
- Not an OCR demo
- Not a document Q&A tool

## What this IS
A schema-driven, autonomous workflow engine that:
1. Accepts a scanned/handwritten document image
2. Checks image quality
3. Runs OCR (EasyOCR)
4. Classifies the document into a known type (resume, employee
   onboarding, student admission, KYC)
5. Loads that document type's schema
6. Extracts structured fields (Gemini Flash) based on the schema
7. Validates extracted fields against the schema's required fields
8. Calculates a confidence score
9. Decides: Approve / Retry OCR / Ask User / Escalate to Human Review
10. Persists full state + audit trail (SQLite + JSON logs)

## Tech Stack
- **Backend:** Python, FastAPI, LangGraph, SQLite, Pydantic
- **AI:** EasyOCR, Gemini Flash (Google Generative AI)
- **Frontend:** React, Vite, TailwindCSS

## Project Structure

```
backend/
    app/
        agents/     # Independent agents (Image Quality, OCR, Classification, Extraction, Validation, Confidence, Decision, Logger)
        harness/    # Governance layer: circuit breaker, health checks, output verification
        graph/      # LangGraph wiring (nodes + edges only, no business logic)
        state/      # WorkflowState — single source of truth
        schemas/    # Document-type schemas (JSON) + Pydantic extraction schema
        services/   # OCR service, LLM service, schema loader
        db/         # SQLite persistence
        core/       # Config loading
        api/        # FastAPI routes
frontend/           # React + Vite + Tailwind UI
docs/                # This documentation set
data/
    uploads/         # Uploaded document images
    logs/            # Per-workflow JSON audit logs
```



## Running the Project

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Backend runs at `http://127.0.0.1:8000`, frontend at `http://localhost:5173`.

## Extensibility

Adding a new document type requires **zero code changes** — only a new
JSON schema file in `backend/app/schemas/`. See `ARCHITECTURE.md` for
details on how this works.

## Documentation Index
- `AGENTS.md` — every agent's responsibilities, inputs, outputs, decision logic
- `TOOLS.md` — external tools/services and how they're wrapped
- `SOUL.md` — the guiding philosophy behind design decisions
- `CLAW.md` — the Harness layer and its relationship to OpenClaw/Hermes concepts
- `STATE.md` — the WorkflowState object and how state flows
- `ARCHITECTURE.md` — full system architecture and diagrams