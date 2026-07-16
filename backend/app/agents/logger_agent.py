import os
import time

from app.state.workflow_state import WorkflowState, HistoryEntry
from app.db.workflow_repository import WorkflowRepository

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)


class LoggerAgent:
    """Persists the full workflow state to a JSON file (audit trail)
    and to SQLite (queryable long-term storage)."""

    name = "LoggerAgent"

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        os.makedirs(LOG_DIR, exist_ok=True)
        log_path = os.path.join(LOG_DIR, f"{state.workflow_id}.json")

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

        WorkflowRepository.save(state)

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"workflow_id={state.workflow_id}",
            output_summary=f"log_written_to={log_path}, sqlite_saved=True",
            duration_ms=duration_ms,
        ))

        return state