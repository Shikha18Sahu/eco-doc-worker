from app.state.workflow_state import WorkflowState
from app.harness.coordinator import HarnessCoordinator
from app.harness.circuit_breaker import CircuitBreaker, CircuitBreakerError

state = WorkflowState(workflow_id="wf-002", document_id="doc-002")
coordinator = HarnessCoordinator()

coordinator.pre_run_check(state)
print("Pre-run check passed.")

try:
    CircuitBreaker.register_retry(state)  # retry_count=1, max_retries=1 -> ok
    CircuitBreaker.register_retry(state)  # retry_count=2 -> exceeds max_retries -> should raise
except CircuitBreakerError as e:
    print("Circuit breaker tripped as expected:", e)

print(state.model_dump_json(indent=2))