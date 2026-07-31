# Lab 3.2 – Dynamic Skill Router

**Objective:** Build a router that inspects the incoming request (or DFD features) and exposes *only* the skills needed for that request, then measure the benefit versus “always attach every tool.”

---

## Learning Goals

- Classify intent with a lightweight, auditable heuristic (rules first; optional LLM classifier later).
- Select a skill subset per class.
- Compare full-tool vs. routed-tool runs on token estimate, number of tools exposed, and outcome correctness.
- Document routing rules so a security reviewer can audit them.

---

## Routing classes (starter)

| Class | When | Skills exposed |
|-------|------|----------------|
| `syntax` | User asks only “is this DFD valid?” | `validate_dfd_syntax` |
| `structural` | Questions about paths / trust boundaries | `validate_dfd_syntax`, `check_trust_boundary_paths` |
| `policy` | Questions about controls / baselines | `match_security_controls` |
| `full` | “Evaluate this DFD for compliance” | All four skills |

---

## Starter Location

```
labs/03-skills/
├── src/
│   └── router.py
├── notebooks/
│   └── lab-3.2-skill-router.ipynb
└── tests/
    └── test_router.py
```

---

## Step-by-Step

### 1. Implement `SkillRouter.classify(request) -> RouteClass`

Start with keyword / feature heuristics (presence of DFD JSON, words like “path”, “control”, “validate only”, …). Keep the function pure and unit-tested.

### 2. Implement `SkillRouter.select(route) -> list[Skill]`

### 3. Side-by-side comparison

For a fixed set of requests, record:

- Tools exposed (count + names)
- Estimated prompt tokens for tool declarations
- Whether the correct skills ran
- Final structured outcome

### 4. Optional hardening

- Reject requests that try to force a high-privilege skill without the matching intent.
- Log every routing decision for audit.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Router returns a deterministic class for the sample requests | Yes |
| Routed runs expose fewer tools than the full set | Yes |
| Unit tests cover each route class | Yes |
| Notebook shows a clear comparison table | Yes |

---

## Submission

Notebook with comparison table + routing rule documentation (bullet list is enough).
