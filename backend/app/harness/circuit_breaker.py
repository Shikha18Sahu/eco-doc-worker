from app.state.workflow_state import WorkflowState, NextAction


class CircuitBreakerError(Exception):
    """Raised only when actively registering a retry that exceeds the limit."""
    pass


class CircuitBreaker:
    """Prevents infinite retry loops by enforcing max_retries on WorkflowState."""

    @staticmethod
    def is_tripped(state: WorkflowState) -> bool:
        """Read-only check — never raises. Safe to call from any node."""
        return state.retry_count > state.max_retries

    @staticmethod
    def register_retry(state: WorkflowState) -> None:
        """Called only from within the OCR retry loop. Raises if the
        retry would exceed the limit, so the caller can stop looping."""
        state.retry_count += 1
        if state.retry_count > state.max_retries:
            state.next_action = NextAction.ESCALATE
            state.human_review_required = True
            raise CircuitBreakerError(
                f"Workflow {state.workflow_id} exceeded max_retries "
                f"({state.retry_count}/{state.max_retries}). Forcing escalation."
            )