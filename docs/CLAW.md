# CLAW — Harness Layer & OpenClaw/Hermes Relationship

## What the Harness Is

The Harness (`app/harness/`) is a governance layer that sits above the
LangGraph-orchestrated agents. LangGraph defines *what paths are
possible*; the Harness decides *whether it's safe to take the next
step*. This mirrors the separation of concerns found in agent harnesses
like OpenClaw/Hermes, where an orchestration layer and a governance
layer are deliberately kept distinct.

## Component-by-Component Mapping

### `coordinator.py` — HarnessCoordinator
Analogous to a **harness's central dispatch loop**. Every node call in
the graph is wrapped by `pre_run_check()` (before) and
`post_run_check()` (after). This is the single place where cross-
cutting governance concerns are enforced, rather than being scattered
across every agent.

### `circuit_breaker.py` — CircuitBreaker
Analogous to a harness's **retry/loop-guard mechanism**. OpenClaw/Hermes-
style harnesses prevent runaway agent loops (an agent calling itself
or another agent indefinitely); here, `CircuitBreaker.register_retry()`
enforces a hard `max_retries` limit on the OCR loop specifically, and
forces an escalation path when exceeded — never an infinite loop, never
a silent crash.

### `health_check.py` — HealthChecker
Analogous to a harness's **tool health verification** step, run before
trusting a tool's output. Currently stubbed for the OCR engine and LLM
service; in a full OpenClaw-style harness this would ping actual
service endpoints before allowing an agent to depend on them.

### `output_verifier.py` — OutputVerifier
Analogous to a harness's **output contract enforcement**. Every agent's
raw output is validated against a Pydantic schema before being trusted
by the next step — this is what prevents malformed LLM output (e.g. a
list where a string was expected) from silently corrupting downstream
state.

## Why This Matters for Future Migration

Because the Harness is a separate layer from the agents and the graph,
migrating to a full OpenClaw/Hermes-based orchestration later would
mean swapping the *coordinator's* internals (e.g. calling into
OpenClaw's native retry/health-check primitives) without needing to
rewrite any agent logic — the agents' contracts (WorkflowState in,
WorkflowState out) remain unchanged.