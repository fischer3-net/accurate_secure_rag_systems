# Lab 3.1 – Modular Skills with Vertex AI Function Calling + Pydantic

**Objective:** Refactor a monolithic “mega-prompt” DFD evaluator into a set of single-responsibility Python skills with clear schemas and structured output validation.

## Deliverables

- At least three skills, e.g.:
  - `validate_dfd_syntax`
  - `match_security_controls`
  - `score_sdlc_compliance`
- Each skill exposed via Vertex AI Function Calling with Pydantic models for inputs/outputs.
- Demonstration that the modular version is more reliable and easier to test than the original mega-prompt.

## Starter Location

```
labs/03-skills/
notebooks/lab-3.1-modular-skills.ipynb
```
