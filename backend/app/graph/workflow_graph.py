from langgraph.graph import StateGraph, END

from app.state.workflow_state import WorkflowState, NextAction
from app.agents.image_quality_agent import ImageQualityAgent
from app.agents.ocr_agent import OCRAgent
from app.agents.classification_agent import ClassificationAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.confidence_agent import ConfidenceAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.logger_agent import LoggerAgent
from app.harness.coordinator import HarnessCoordinator
from app.harness.circuit_breaker import CircuitBreaker, CircuitBreakerError

coordinator = HarnessCoordinator()
image_quality_agent = ImageQualityAgent()
ocr_agent = OCRAgent()
classification_agent = ClassificationAgent()
extraction_agent = ExtractionAgent()
validation_agent = ValidationAgent()
confidence_agent = ConfidenceAgent()
decision_agent = DecisionAgent()
logger_agent = LoggerAgent()


def image_quality_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = image_quality_agent.run(state)
    coordinator.post_run_check(state)
    return state


def ocr_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = ocr_agent.run(state)
    coordinator.post_run_check(state)

    if state.next_action == NextAction.RETRY_OCR:
        try:
            CircuitBreaker.register_retry(state)
        except CircuitBreakerError:
            pass

    return state


def classification_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = classification_agent.run(state)
    coordinator.post_run_check(state)
    return state


def extraction_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = extraction_agent.run(state)
    coordinator.post_run_check(state)
    return state


def validation_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = validation_agent.run(state)
    coordinator.post_run_check(state)
    return state


def confidence_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = confidence_agent.run(state)
    coordinator.post_run_check(state)
    return state


def decision_node(state: WorkflowState) -> WorkflowState:
    coordinator.pre_run_check(state)
    state = decision_agent.run(state)
    coordinator.post_run_check(state)
    return state


def logger_node(state: WorkflowState) -> WorkflowState:
    state = logger_agent.run(state)
    return state


def route_after_ocr(state: WorkflowState) -> str:
    if state.next_action == NextAction.RETRY_OCR:
        return "ocr"
    return "classification"


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("image_quality", image_quality_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("classification", classification_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("validation", validation_node)
    graph.add_node("confidence_scoring", confidence_node)
    graph.add_node("decision", decision_node)
    graph.add_node("logger", logger_node)

    graph.set_entry_point("image_quality")
    graph.add_edge("image_quality", "ocr")
    graph.add_conditional_edges("ocr", route_after_ocr, {"ocr": "ocr", "classification": "classification"})
    graph.add_edge("classification", "extraction")
    graph.add_edge("extraction", "validation")
    graph.add_edge("validation", "confidence_scoring")
    graph.add_edge("confidence_scoring", "decision")
    graph.add_edge("decision", "logger")
    graph.add_edge("logger", END)

    return graph.compile()