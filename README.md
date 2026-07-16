# Autonomous AI Document Processing Worker

An autonomous AI worker that owns an entire document-processing business
workflow — from image upload to a final Approve / Retry / Ask-User /
Escalate decision — rather than a single LLM call wrapped in an API.

## What this IS

A schema-driven, autonomous workflow engine that:
1. Accepts a scanned/handwritten document image
2. Checks image quality (blur + resolution, via OpenCV)
3. Runs OCR (EasyOCR)
4. Classifies the document into a known type (resume, employee
   onboarding, student admission, KYC) — or gracefully flags it as
   unknown if it matches none
5. Loads that document type's schema
6. Extracts structured fields (Gemini Flash) based on the schema
7. Validates extracted fields against the schema's required fields
8. Calculates a confidence score
9. Decides: Approve / Retry OCR / Ask User / Escalate to Human Review
10. If "Ask User" is decided, allows the user to supply the missing
    field(s) via the frontend and re-validates without re-running
    OCR/extraction
11. Persists full state + audit trail (SQLite + JSON logs)

## Tech Stack

- **Backend:** Python, FastAPI, LangGraph, SQLite, Pydantic
- **AI:** EasyOCR, Gemini Flash (Google Generative AI)
- **Frontend:** React, Vite, TailwindCSS
- **Deployment:** Docker + Docker Compose

## Project Structure

```
backend/
    app/
        agents/
        harness/
        graph/
        state/
        schemas/
        services/
        db/
        core/
        api/
frontend/
docs/
docker/
data/
    uploads/
    logs/
```
## Running the Project

### Option A — Local (no Docker)

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

### Option B — Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

Backend: `http://127.0.0.1:8000` · Frontend: `http://127.0.0.1:5173`

### Required Environment Variable

Create `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
```

## Extensibility

Adding a new document type requires **zero code changes** — only a new
JSON schema file in `backend/app/schemas/`. See `docs/ARCHITECTURE.md`
for how this works.

## Documentation Index

Core architecture:
- [`docs/AGENTS.md`](docs/AGENTS.md) — every agent's responsibilities, inputs, outputs, decision logic
- [`docs/TOOLS.md`](docs/TOOLS.md) — external tools/services and how they're wrapped
- [`docs/SOUL.md`](docs/SOUL.md) — the guiding philosophy behind design decisions
- [`docs/CLAW.md`](docs/CLAW.md) — the Harness layer and its relationship to OpenClaw/Hermes concepts
- [`docs/STATE.md`](docs/STATE.md) — the WorkflowState object and how state flows
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — full system architecture and diagrams
- [`docs/LANGGRAPH_ARCHITECTURE.md`](docs/LANGGRAPH_ARCHITECTURE.md) — graph structure, node/edge design, lessons learned
- [`docs/OPENCLAW_HERMES_MAPPING.md`](docs/OPENCLAW_HERMES_MAPPING.md) — component mapping + migration plan

Workflow & behavior:
- [`docs/WORKFLOW.md`](docs/WORKFLOW.md) — pipeline stages and conditional branches
- [`docs/MEMORY_STRATEGY.md`](docs/MEMORY_STRATEGY.md) — short-term and long-term memory design
- [`docs/RETRY_STRATEGY.md`](docs/RETRY_STRATEGY.md) — OCR retry logic and circuit breaker
- [`docs/EXCEPTION_HANDLING.md`](docs/EXCEPTION_HANDLING.md) — where and how failures are caught
- [`docs/ESCALATION_POLICY.md`](docs/ESCALATION_POLICY.md) — when the system escalates vs. asks vs. approves
- [`docs/AUDIT_LOGGING.md`](docs/AUDIT_LOGGING.md) — what's logged, where, and why
- [`docs/CURRENT_AUTONOMY.md`](docs/CURRENT_AUTONOMY.md) — what the system does without human input today

Reference & examples:
- [`docs/API.md`](docs/API.md) — endpoint documentation
- [`docs/INPUT_OUTPUT_EXAMPLES.md`](docs/INPUT_OUTPUT_EXAMPLES.md) — real request/response examples
- [`docs/FUTURE_IMPROVEMENTS.md`](docs/FUTURE_IMPROVEMENTS.md) — known limitations and next steps

Developed by Shikha Sahu
