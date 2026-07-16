from app.harness.circuit_breaker import CircuitBreaker
from app.harness.health_check import HealthChecker
from app.state.workflow_state import WorkflowState


class HarnessCoordinator:
    """Central governor. Every agent call in the LangGraph nodes must be
    wrapped by this coordinator before/after execution."""

    def pre_run_check(self, state: WorkflowState) -> None:
        """Called before an agent runs. Read-only checks only — never
        raises due to retry limits (that's handled inside the OCR node
        specifically, via CircuitBreaker.register_retry)."""
        statuses = HealthChecker.check_all()
        for s in statuses:
            if not s.healthy:
                raise RuntimeError(f"Tool unhealthy: {s.tool_name} - {s.detail}")

    def post_run_check(self, state: WorkflowState) -> None:
        pass