# import time

# from app.state.workflow_state import (
#     WorkflowState, WorkflowStatus, HistoryEntry, NextAction
# )

# CONFIDENCE_APPROVE_THRESHOLD = 0.75
# CONFIDENCE_ASK_USER_THRESHOLD = 0.5


# class DecisionAgent:
#     """Decides the final outcome of the workflow based on confidence
#     and validation_errors. This is the single place business rules
#     for approve/retry/ask_user/escalate live."""

#     name = "DecisionAgent"

#     def run(self, state: WorkflowState) -> WorkflowState:
#         start = time.perf_counter()

#         state.status = WorkflowStatus.DECIDING
#         state.current_step = "decision"

#         confidence = state.confidence or 0.0
#         has_errors = len(state.validation_errors) > 0

#         if has_errors and confidence < CONFIDENCE_ASK_USER_THRESHOLD:
#             decision = NextAction.ESCALATE
#             state.human_review_required = True
#             state.status = WorkflowStatus.ESCALATED
#         elif has_errors:
#             decision = NextAction.ASK_USER
#             state.status = WorkflowStatus.AWAITING_USER_INPUT
#         elif confidence >= CONFIDENCE_APPROVE_THRESHOLD:
#             decision = NextAction.APPROVE
#             state.status = WorkflowStatus.APPROVED
#         else:
#             decision = NextAction.ESCALATE
#             state.human_review_required = True
#             state.status = WorkflowStatus.ESCALATED

#         state.next_action = decision

#         duration_ms = (time.perf_counter() - start) * 1000

#         state.add_history(HistoryEntry(
#             agent=self.name,
#             input_summary=f"confidence={confidence}, validation_errors={len(state.validation_errors)}",
#             output_summary=f"decision={decision.value}",
#             decision=decision.value,
#             confidence=confidence,
#             duration_ms=duration_ms,
#         ))

#         return state



import time

from app.state.workflow_state import (
    WorkflowState, WorkflowStatus, HistoryEntry, NextAction
)
from app.services.schema_loader import SchemaLoader

CONFIDENCE_APPROVE_THRESHOLD = 0.75
CONFIDENCE_ASK_USER_THRESHOLD = 0.5

UNKNOWN_TYPE_MESSAGE = (
    "Unknown document type. No validation schema available. "
    "Escalating for human review."
)


class DecisionAgent:
    """Decides the final outcome of the workflow. Handles the special
    'unknown document type' case as a graceful, explicit escalation —
    never a guess, never a generic error."""

    name = "DecisionAgent"

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.DECIDING
        state.current_step = "decision"

        document_type = state.structured_data.get("_document_type", "unknown")
        schema = SchemaLoader.get_schema(document_type)

        # --- Special case: unknown document type, handled first and
        # separately from normal confidence/validation logic ---
        if schema is None:
            decision = NextAction.ESCALATE
            state.human_review_required = True
            state.status = WorkflowStatus.ESCALATED

            if UNKNOWN_TYPE_MESSAGE not in state.validation_errors:
                state.validation_errors.append(UNKNOWN_TYPE_MESSAGE)

            state.next_action = decision

            duration_ms = (time.perf_counter() - start) * 1000
            state.add_history(HistoryEntry(
                agent=self.name,
                input_summary=f"document_type={document_type}",
                output_summary=UNKNOWN_TYPE_MESSAGE,
                decision=decision.value,
                duration_ms=duration_ms,
            ))
            return state

        # --- Normal decision logic for known, schema-matched documents ---
        confidence = state.confidence or 0.0
        has_errors = len(state.validation_errors) > 0

        if has_errors and confidence < CONFIDENCE_ASK_USER_THRESHOLD:
            decision = NextAction.ESCALATE
            state.human_review_required = True
            state.status = WorkflowStatus.ESCALATED
        elif has_errors:
            decision = NextAction.ASK_USER
            state.status = WorkflowStatus.AWAITING_USER_INPUT
        elif confidence >= CONFIDENCE_APPROVE_THRESHOLD:
            decision = NextAction.APPROVE
            state.status = WorkflowStatus.APPROVED
        else:
            decision = NextAction.ESCALATE
            state.human_review_required = True
            state.status = WorkflowStatus.ESCALATED

        state.next_action = decision

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"confidence={confidence}, validation_errors={len(state.validation_errors)}",
            output_summary=f"decision={decision.value}",
            decision=decision.value,
            confidence=confidence,
            duration_ms=duration_ms,
        ))

        return state