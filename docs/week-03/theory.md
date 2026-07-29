# Week 3 Theory – Skill Architecture & Prompt Hygiene

!!! note "Status"
    Skeleton. Expand with concrete before/after prompt examples and token-count measurements.

## Anatomy of a Skill

- System prompt vs. retrieval context vs. tool/function definitions.
- JSON schema + docstring best practices for Vertex AI Function Calling.
- Structured outputs with Pydantic.

## Defeating Skill and Prompt Bloat

- Why 20+ tools destroy reasoning accuracy and cause tool hallucination.
- Dynamic skill routing / specialized sub-agents (`DiagramSyntaxValidator`, `SecurityPolicyMatcher`, `SDLCGateChecker`).
- Context-window budgeting, progressive disclosure, summary buffers.

## Security & Prompt Injection Defenses

- Indirect prompt injection via untrusted user diagrams or third-party specs.
- Principle of least privilege for autonomous tools.
- Output validation and allow-listing of tool side-effects.
