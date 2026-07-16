# Retry Strategy

## What Gets Retried

Only OCR. Nothing else in the pipeline retries automatically.

## Trigger Condition

`OCRAgent` sets `next_action = RETRY_OCR` if OCR confidence is below `0.6`.

## Enforcement

The retry loop is NOT self-governed by the OCR agent. The `ocr_node` function in `workflow_graph.py` calls `CircuitBreaker.register_retry(state)` after every OCR run that requested a retry. This:
1. Increments `state.retry_count`
2. Checks it against `state.max_retries` (default: `1`)
3. If exceeded, forces `next_action = ESCALATE` and raises internally (caught by the node, not propagated as a crash)

The graph's conditional edge (`route_after_ocr`) then reads `next_action` — a pure, read-only decision — to decide whether to loop back to the OCR node or proceed to classification.

## Why Retry Logic Lives in the Node, Not the Router

An earlier version of this project put the retry-count increment inside the LangGraph conditional-edge function. This caused an infinite loop (`GraphRecursionError`) because LangGraph conditional-edge functions are read-only — any state mutation performed there is silently discarded and never persisted. The fix: state mutations only ever happen inside real graph nodes, never inside routing functions. This is documented as a lesson learned, not just a design choice.

## Why Only One Retry

Business rule per the assignment spec: never retry forever. One retry balances giving OCR a second chance (useful when a scan has transient noise) against not wasting compute/time on a fundamentally unreadable image — which should instead go to a human reviewer.