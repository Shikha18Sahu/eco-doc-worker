import json

from app.db.database import get_connection
from app.state.workflow_state import WorkflowState


class WorkflowRepository:
    """Persists WorkflowState to SQLite. This is the long-term
    persistence layer — the Logger Agent writes JSON files for
    audit trail; this repository writes queryable rows for lookups."""

    @staticmethod
    def save(state: WorkflowState) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workflows (
                workflow_id, document_id, status, next_action, confidence,
                human_review_required, structured_data, validation_errors,
                state_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(workflow_id) DO UPDATE SET
                status=excluded.status,
                next_action=excluded.next_action,
                confidence=excluded.confidence,
                human_review_required=excluded.human_review_required,
                structured_data=excluded.structured_data,
                validation_errors=excluded.validation_errors,
                state_json=excluded.state_json,
                updated_at=excluded.updated_at
        """, (
            state.workflow_id,
            state.document_id,
            state.status.value,
            state.next_action.value,
            state.confidence,
            int(state.human_review_required),
            json.dumps(state.structured_data),
            json.dumps(state.validation_errors),
            state.model_dump_json(),
            state.created_at.isoformat(),
            state.updated_at.isoformat(),
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get(workflow_id: str) -> dict | None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflows WHERE workflow_id = ?", (workflow_id,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)