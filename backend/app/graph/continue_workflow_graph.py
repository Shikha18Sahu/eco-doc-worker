from langgraph.graph import StateGraph, END

from app.state.workflow_state import WorkflowState
from app.graph.workflow_graph import validation_node, confidence_node, decision_node, logger_node


def build_continue_workflow_graph():
    """A shorter graph used when continuing a workflow after the user
    supplies missing fields. Works for ANY document type — skips
    OCR/classification/extraction, only re-validates, re-scores, and
    re-decides based on the already-classified document's schema."""
    graph = StateGraph(WorkflowState)

    graph.add_node("validation", validation_node)
    graph.add_node("confidence_scoring", confidence_node)
    graph.add_node("decision", decision_node)
    graph.add_node("logger", logger_node)

    graph.set_entry_point("validation")
    graph.add_edge("validation", "confidence_scoring")
    graph.add_edge("confidence_scoring", "decision")
    graph.add_edge("decision", "logger")
    graph.add_edge("logger", END)

    return graph.compile()