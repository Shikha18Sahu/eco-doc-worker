import json
import re
import time

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry
from app.services.schema_loader import SchemaLoader
from app.services.llm_service import LLMService

CLASSIFICATION_PROMPT = """You are a strict document classification engine.

Given raw OCR text from a scanned/handwritten document, classify it into
EXACTLY ONE of the following document types:
{known_types}

Rules:
- Return ONLY valid JSON, no markdown, no explanation, no backticks.
- If the text clearly matches one of the listed types, return that type.
- If the text does not clearly match ANY of the listed types, return "unknown".
- Do not invent a new type. Only choose from the list above, or "unknown".

OCR TEXT:
{ocr_text}

Return JSON in this exact shape:
{{"document_type": "..."}}
"""


class ClassificationAgent:
    """Classifies the document into one of the known schema types
    (loaded dynamically from SchemaLoader), or 'unknown' if it doesn't
    match any registered schema. This agent never invents new types —
    it can only pick from what SchemaLoader knows about."""

    name = "ClassificationAgent"

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.EXTRACTING  # reuse; could add a CLASSIFYING status later
        state.current_step = "classification"

        known_types = SchemaLoader.list_known_types()
        raw_text = state.raw_ocr_text or ""

        classified_type = "unknown"
        error = None

        if raw_text.strip() and known_types:
            try:
                prompt = CLASSIFICATION_PROMPT.format(
                    known_types=", ".join(known_types),
                    ocr_text=raw_text,
                )
                response = self.llm_service.model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.0},
                )
                text = response.text.strip()
                text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
                parsed = json.loads(text)
                candidate = parsed.get("document_type", "unknown")

                # Never trust the LLM blindly — only accept it if it's
                # actually a known type. Anything else collapses to "unknown".
                classified_type = candidate if candidate in known_types else "unknown"

            except Exception as e:
                error = str(e)
                classified_type = "unknown"

        state.structured_data["_document_type"] = classified_type

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"known_types={known_types}",
            output_summary=f"classified_type={classified_type}",
            duration_ms=duration_ms,
            error=error,
        ))

        return state