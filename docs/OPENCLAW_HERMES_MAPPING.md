# Mapping to OpenClaw/Hermes & Migration Plan

## Current Mapping (also see `CLAW.md`)

| This Project | OpenClaw/Hermes Concept |
|---|---|
| `HarnessCoordinator.pre_run_check` / `post_run_check` | Central dispatch/governance loop wrapping every tool/agent call |
| `CircuitBreaker` | Retry/loop-guard mechanism preventing runaway agent loops |
| `HealthChecker` | Tool health verification before trusting a tool's output |
| `OutputVerifier` | Output-contract enforcement — validating a tool/agent's output shape before accepting it |
| `WorkflowState` | The harness's shared execution context / scratchpad passed between steps |
| LangGraph's node/edge graph | The harness's orchestration/execution-plan layer |

## What Would Be Required to Migrate

1. **Replace `HarnessCoordinator` internals** with calls into OpenClaw's native dispatch primitives, while keeping its public interface (`pre_run_check`, `post_run_check`) unchanged — agent code and LangGraph node functions would not need to change.
2. **Replace `CircuitBreaker`** with OpenClaw's native retry/loop-guard configuration, likely expressed as policy config rather than Python logic — the `max_retries` field on `WorkflowState` would map directly to such a policy value.
3. **Replace `HealthChecker` stubs** with OpenClaw's real tool-health-check primitives, since this project's version is currently a placeholder that always returns healthy.
4. **Keep `OutputVerifier`** largely as-is — Pydantic-based schema verification is a reasonable fit regardless of the underlying orchestration engine.
5. **Keep all 8 agents and `WorkflowState` unchanged** — since the Harness is a separate layer by design (see `SOUL.md`, principle 6), migrating the orchestration/governance backend should not require touching agent business logic at all. This separation is the actual point of building the Harness as its own layer instead of embedding governance logic inside LangGraph nodes directly.
6. **LangGraph itself could either stay** (if OpenClaw supports wrapping an existing LangGraph graph) **or be replaced** with OpenClaw's native execution-plan format — this is the one area where meaningful rework would be needed, since node/edge definitions are LangGraph-specific syntax.

## Why This Matters

This mapping is what allows the project to credibly claim "designed for future migration to OpenClaw" — not because OpenClaw integration code already exists, but because the architecture's separation of concerns (agents vs. graph vs. harness) means such a migration is a bounded, identifiable piece of work rather than a full rewrite.