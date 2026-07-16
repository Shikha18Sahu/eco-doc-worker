# # import time

# # from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry

# # REQUIRED_FIELDS = ["name", "amount"]


# # class ValidationAgent:
# #     """Checks that mandatory fields are present in structured_data.
# #     Appends to validation_errors if any are missing."""

# #     name = "ValidationAgent"

# #     def run(self, state: WorkflowState) -> WorkflowState:
# #         start = time.perf_counter()

# #         state.status = WorkflowStatus.VALIDATING
# #         state.current_step = "validation"

# #         missing = [
# #             field for field in REQUIRED_FIELDS
# #             if not state.structured_data.get(field)
# #         ]

# #         for field in missing:
# #             state.validation_errors.append(f"Missing mandatory field: {field}")

# #         duration_ms = (time.perf_counter() - start) * 1000

# #         state.add_history(HistoryEntry(
# #             agent=self.name,
# #             input_summary=f"structured_data={state.structured_data}",
# #             output_summary=f"missing_fields={missing}" if missing else "all mandatory fields present",
# #             decision="fail" if missing else "pass",
# #             duration_ms=duration_ms,
# #         ))

# #         return state






# import time

# from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry


# class ValidationAgent:
#     """Schema-free validation: checks that every field the LLM detected
#     actually has a non-null value, and that at least one field was
#     extracted at all. Fixed 'mandatory field' checks don't apply here
#     since the field set is dynamic per document."""

#     name = "ValidationAgent"

#     def run(self, state: WorkflowState) -> WorkflowState:
#         start = time.perf_counter()

#         state.status = WorkflowStatus.VALIDATING
#         state.current_step = "validation"

#         visible_fields = {
#             k: v for k, v in state.structured_data.items() if not k.startswith("_")
#         }

#         if not visible_fields:
#             state.validation_errors.append("No fields were extracted from the document")
#         else:
#             for field_name, value in visible_fields.items():
#                 if value is None or str(value).strip() == "":
#                     state.validation_errors.append(f"Field '{field_name}' has no value")

#         duration_ms = (time.perf_counter() - start) * 1000

#         state.add_history(HistoryEntry(
#             agent=self.name,
#             input_summary=f"structured_data={visible_fields}",
#             output_summary=(
#                 f"validation_errors={state.validation_errors}"
#                 if state.validation_errors else "all extracted fields have values"
#             ),
#             decision="fail" if state.validation_errors else "pass",
#             duration_ms=duration_ms,
#         ))

#         return state


import time

from app.state.workflow_state import WorkflowState, WorkflowStatus, HistoryEntry
from app.services.schema_loader import SchemaLoader


class ValidationAgent:
    """Validates extracted fields against the matched schema's
    required_fields. If no schema was matched (unknown document type),
    validation is skipped entirely — DecisionAgent handles that case
    with its own explicit graceful message."""

    name = "ValidationAgent"

    def run(self, state: WorkflowState) -> WorkflowState:
        start = time.perf_counter()

        state.status = WorkflowStatus.VALIDATING
        state.current_step = "validation"

        document_type = state.structured_data.get("_document_type", "unknown")
        schema = SchemaLoader.get_schema(document_type)

        visible_fields = {
            k: v for k, v in state.structured_data.items() if not k.startswith("_")
        }

        if schema is None:
            duration_ms = (time.perf_counter() - start) * 1000
            state.add_history(HistoryEntry(
                agent=self.name,
                input_summary=f"document_type={document_type}",
                output_summary="No schema available — validation skipped",
                duration_ms=duration_ms,
            ))
            return state

        required_fields = schema.get("required_fields", [])
        missing = [f for f in required_fields if not visible_fields.get(f)]
        for f in missing:
            state.validation_errors.append(f"Missing mandatory field: {f}")

        duration_ms = (time.perf_counter() - start) * 1000

        state.add_history(HistoryEntry(
            agent=self.name,
            input_summary=f"document_type={document_type}, extracted={visible_fields}",
            output_summary=(
                f"validation_errors={state.validation_errors}"
                if state.validation_errors else "all required fields present"
            ),
            decision="fail" if state.validation_errors else "pass",
            duration_ms=duration_ms,
        ))

        return state