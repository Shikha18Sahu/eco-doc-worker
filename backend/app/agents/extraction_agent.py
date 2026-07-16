import time

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry
from app.services.llm_service import LLMService
from app.services.schema_loader import SchemaLoader
from app.harness.output_verifier import OutputVerifier, OutputVerificationError
from app.schemas.extracted_document import ExtractedDocument


def _normalize_value(value):
    """Lists become a single readable string; everything else passes through."""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value if v is not None)
    return value


class ExtractionAgent:
    name = "ExtractionAgent"

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.EXTRACTING
        state.current_step = "extraction"

        internal_keys = {
            k: v for k, v in state.structured_data.items() if k.startswith("_")
        }

        document_type = internal_keys.get("_document_type", "unknown")
        schema = SchemaLoader.get_schema(document_type)

        if schema is None:
            state.structured_data = {**internal_keys}
            duration_ms = (time.perf_counter() - start) * 1000
            state.add_history(HistoryEntry(
                agent=self.name,
                input_summary=f"document_type={document_type}",
                output_summary="No schema available — extraction skipped",
                duration_ms=duration_ms,
            ))
            return state

        all_fields = schema["required_fields"] + schema.get("optional_fields", [])
        raw_fields = self.llm_service.extract_fields_with_schema(
            state.raw_ocr_text or "", all_fields
        )

        error = None
        try:
            verified = OutputVerifier.verify(raw_fields, ExtractedDocument)
            normalized = {
                k: _normalize_value(v) for k, v in verified.model_dump().items()
            }
            state.structured_data = {**internal_keys, **normalized}
        except OutputVerificationError as e:
            # Don't discard everything — fall back to raw (normalized)
            # values so a single bad field doesn't wipe good extractions.
            error = str(e)
            normalized = {k: _normalize_value(v) for k, v in raw_fields.items()}
            state.structured_data = {**internal_keys, **normalized}
            state.validation_errors.append(f"Extraction output partially invalid: {error}")

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"document_type={document_type}, expected_fields={all_fields}",
            output_summary=f"structured_data={state.structured_data}",
            duration_ms=duration_ms,
            error=error,
        ))

        return state