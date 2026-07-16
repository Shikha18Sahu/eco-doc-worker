# Exception Handling

## Principle

Failures inside agents should degrade gracefully into a workflow state (`escalated`, with a clear `validation_errors` message) rather than propagating as unhandled exceptions / HTTP 500s, wherever the failure is something the business logic can reasonably anticipate.

## Where Exceptions Are Caught

| Location | What's Caught | Result |
|---|---|---|
| `ClassificationAgent.run()` | Any Gemini API error | Defaults to `"unknown"` document type — graceful, not a crash |
| `ExtractionAgent.run()` | `OutputVerificationError` (schema mismatch) | Falls back to normalized raw values instead of discarding all extracted data |
| `LLMService.extract_fields_with_schema()` | Any Gemini API error | Returns all-null fields dict; logged to console for debugging |
| `ocr_node()` | `CircuitBreakerError` | Caught locally; `next_action` was already set to `ESCALATE` before the exception was raised, so the workflow continues gracefully to the decision stage |

## Where Exceptions Are Allowed to Propagate

`HarnessCoordinator.pre_run_check()` raises `RuntimeError` if a tool health check fails (currently stubbed to always pass). This is intentionally NOT caught at the node level — a genuinely unhealthy tool (e.g. OCR engine unreachable) should stop the workflow loudly rather than silently producing garbage output.

## Lesson Learned: Don't Over-Catch

An earlier version had `CircuitBreaker.check()` called unconditionally in every node's `pre_run_check()`, which meant that once a workflow's retry count exceeded the limit, every subsequent node (extraction, validation, etc.) would raise an uncaught `CircuitBreakerError` and crash the whole request with a 500. The fix: circuit-breaker enforcement was narrowed to only the OCR retry path specifically, and `pre_run_check()` was made read-only-safe for all other nodes. This is documented here because it's a good example of a real bug found and fixed during development, not a design that worked perfectly the first time.