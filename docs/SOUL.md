# SOUL — Guiding Philosophy

This document captures the *why* behind the architecture, not the *how*.

## 1. The system should never guess
If a document type is unknown, the system says so explicitly and
escalates — it does not force-fit the document into the nearest
schema. If a required field is missing, the system says which field
and why — it does not silently approve incomplete data.

## 2. Business rules belong in data, not code
Required fields, optional fields, and validation types live in JSON
schema files — not hardcoded in Python. This means the engineering
team can add a new document type without touching agent code, and
the business/product team can reason about "what's required for a
KYC form" by reading a JSON file, not by reading Python.

## 3. One bad field should never destroy good data
Early in this project, a single malformed field (a list where a string
was expected) caused the entire extraction to be discarded — including
fields that were correctly extracted. This was treated as a real bug
and fixed: agents fall back to partial, normalized results rather than
all-or-nothing failure.

## 4. The system should explain itself
Every agent appends a `HistoryEntry` to the workflow's audit trail —
what it did, why, and how confident it was. This isn't an afterthought;
it's how a human reviewer (or a future engineer) understands what
happened to a specific document without re-running it.

## 5. Retry, but not forever
Autonomy does not mean unconditional persistence. OCR is retried
exactly once; if confidence remains low, the system escalates rather
than looping. This is enforced structurally (the Harness's
CircuitBreaker), not by convention.

## 6. Governance is separate from execution
Agents do the work. The Harness decides whether the work is allowed to
continue. This separation means retry limits, health checks, and
output verification can be reasoned about and modified independently
of any single agent's logic.