import time

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry


class ConfidenceAgent:
    """Combines OCR confidence with validation results to produce a
    final confidence score used by the Decision Agent."""

    name = "ConfidenceAgent"

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.SCORING_CONFIDENCE
        state.current_step = "confidence_scoring"

        base_confidence = state.confidence or 0.0
        penalty = 0.15 * len(state.validation_errors)
        final_confidence = max(0.0, base_confidence - penalty)

        state.confidence = round(final_confidence, 2)

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"base_confidence={base_confidence}, validation_errors={len(state.validation_errors)}",
            output_summary=f"final_confidence={state.confidence}",
            confidence=state.confidence,
            duration_ms=duration_ms,
        ))

        return state