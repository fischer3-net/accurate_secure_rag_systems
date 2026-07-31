# Lab 3.1 – Modular Skills with Pydantic & Function-Calling Contracts

**Objective:** Replace a monolithic “mega-prompt” DFD evaluator with a set of single-responsibility Python skills that have clear input/output schemas and can be exposed to Vertex AI Function Calling.

---

## Learning Goals

- Define Pydantic models for skill arguments and return values.
- Implement at least four skills that cover syntax, structural, policy, and scoring concerns.
- Register skills in a registry that emits Vertex-compatible tool declarations.
- Show that modular skills are independently testable and produce structured results.

---

## Skills to implement (starter set)

| Skill | Responsibility | LLM required? |
|-------|----------------|---------------|
| `validate_dfd_syntax` | Schema / referential integrity of DFD JSON | No |
| `check_trust_boundary_paths` | Graph paths ExternalEntity → DataStore crossing trust boundaries | No |
| `match_security_controls` | Hybrid retrieval of governing controls for a question or element | Optional |
| `score_sdlc_compliance` | Aggregate pass/fail + risk summary from prior skill outputs | No (rules) |

Deterministic skills are preferred for security-critical checks; LLM-backed skills stay behind a clear boundary.

---

## Starter Location

```
labs/03-skills/
├── src/
│   ├── schemas.py          # shared Pydantic models
│   ├── skills_syntax.py
│   ├── skills_graph.py
│   ├── skills_policy.py
│   ├── skills_score.py
│   ├── registry.py         # tool declarations + dispatch
│   └── mega_prompt.py      # baseline “bad” implementation for contrast
├── notebooks/
│   └── lab-3.1-modular-skills.ipynb
└── tests/
    └── test_skills.py
```

---

## Step-by-Step

### 1. Inspect the mega-prompt baseline

`mega_prompt.py` contains a single function that stuffs the entire DFD + a long instruction block into one string and pretends to “evaluate” it. Note the problems: untestable, unbounded tokens, no structured output, injection surface.

### 2. Implement the four skills

Each skill:

- Accepts a Pydantic input model,
- Returns a Pydantic output model,
- Raises or returns a typed error on invalid input (never free-text failure modes).

### 3. Register tools

```python
from src.registry import SkillRegistry
reg = SkillRegistry()
reg.register(validate_dfd_syntax)
reg.register(check_trust_boundary_paths)
# ...
tools = reg.vertex_tool_declarations()  # list[dict] for Function Calling
```

### 4. Run end-to-end on the sample DFD

Produce a structured report without a single mega-prompt.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| ≥ 4 skills with Pydantic I/O | Yes |
| Registry emits valid tool JSON schemas | Yes |
| All skills unit-tested | Yes |
| Sample DFD produces a structured compliance-style result | Yes |
| Mega-prompt baseline retained for contrast | Yes |

---

## Submission

Notebook + any skill extensions; short note on which skills you would keep deterministic vs. LLM-backed in production.
