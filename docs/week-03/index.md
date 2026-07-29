# Week 3 – Skill Architecture, Tooling & Curing Prompt/Skill Bloat

**Focus:** Designing clean, single-purpose skills/tools in Python while preventing token bloat, tool confusion, and context drift.

## Learning Outcomes

- Distinguish System Prompts, Retrieval Augmentation, and Agentic Tools/Skills.
- Define clear JSON schemas and docstrings for Vertex AI Function Calling.
- Avoid the “tool overload” problem through dynamic skill routing / orchestration.
- Apply least-privilege and prompt-injection defenses for skills that process untrusted DFDs.

## Agenda

1. Theory – Anatomy of a skill, bloat mitigation, security
2. Lab 3.1 – Refactor monolithic mega-prompt into modular skills + Pydantic validation
3. Lab 3.2 – Dynamic Skill Router based on input classification

## Navigation

- [Theory](theory.md)
- [Lab 3.1](lab-3.1.md)
- [Lab 3.2](lab-3.2.md)
