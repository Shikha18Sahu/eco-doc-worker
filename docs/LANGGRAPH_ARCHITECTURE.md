# LangGraph Architecture Explanation

## Why LangGraph

LangGraph models the workflow as an explicit state machine: nodes are functions that take a `WorkflowState` and return a `WorkflowState`; edges (including conditional edges) define which node runs next. This makes the "possible paths" through the workflow explicit and inspectable, rather than buried in nested if/else logic.

## Graph Structure (`app/graph/workflow_graph.py`)

**Nodes:**
`image_quality` → `ocr` → `classification` → `extraction` → `validation` → `confidence_scoring` → `decision` → `logger`

**Conditional edge:** only one exists, after `ocr`:
route_after_ocr(state):
if state.next_action == RETRY_OCR:
return "ocr"     # loop back
return "classification"

All other edges are fixed (`add_edge`), since only the OCR stage has a legitimate reason to repeat.

## Key Implementation Detail: Node Name vs. State Field Collision

LangGraph node names share a namespace with the `WorkflowState`'s field names. Naming a node `"confidence"` (matching the `confidence: float` field on `WorkflowState`) caused a `ValueError: 'confidence' is already being used as a state key`. Fix: the node was renamed to `"confidence_scoring"`. This is a real constraint worth knowing before naming nodes in any LangGraph project.

## Key Implementation Detail: Conditional Edges Are Read-Only

State mutations inside a conditional-edge function (like incrementing `retry_count`) are **not persisted** by LangGraph — only mutations returned from actual node functions are. An earlier version put `CircuitBreaker.register_retry()` inside the conditional-edge function, causing `retry_count` to never actually increment and the graph to loop until hitting LangGraph's default recursion limit (25). Fix: the retry-count mutation moved into the `ocr_node` function itself; the conditional edge only reads `next_action`, never mutates state.

## Harness Wrapping Pattern

Every node function follows the same wrapper pattern:
def some_node(state):
coordinator.pre_run_check(state)   # Harness governance, before
state = some_agent.run(state)      # actual agent logic
coordinator.post_run_check(state)  # Harness governance, after
return state
This keeps LangGraph's job purely orchestration, and the Harness's job purely governance — see `CLAW.md`.