import time

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry, NextAction
from app.services.ocr_service import OCRService


class OCRAgent:
    """Runs real OCR on the uploaded document image."""

    name = "OCRAgent"

    def __init__(self, ocr_service: OCRService | None = None):
        self.ocr_service = ocr_service or OCRService()

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.RUNNING_OCR
        state.current_step = "ocr"

        attempt = state.retry_count + 1
        image_path = state.structured_data.get("_image_path")

        if not image_path:
            state.validation_errors.append("No image path found for OCR")
            state.confidence = 0.0
            state.next_action = NextAction.ESCALATE
            duration_ms = (time.perf_counter() - start) * 1000
            state.add_history(HistoryEntry(
                agent=self.name,
                input_summary="missing image_path",
                output_summary="OCR skipped, no image",
                duration_ms=duration_ms,
                error="missing image_path",
            ))
            return state

        text, ocr_confidence = self.ocr_service.extract_text(image_path, attempt)

        state.raw_ocr_text = text
        state.confidence = ocr_confidence

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"image_path={image_path}, attempt={attempt}",
            output_summary=f"ocr_confidence={ocr_confidence}, text_len={len(text)}",
            confidence=ocr_confidence,
            duration_ms=duration_ms,
        ))

        if ocr_confidence < 0.6:
            state.next_action = NextAction.RETRY_OCR
        else:
            state.next_action = NextAction.NONE

        return state