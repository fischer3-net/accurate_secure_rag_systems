# Lab EC.1 – Canonical DFD Schema, Validation & Controlled Conversion

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/extra-credit/notebooks/lab-ec.1-canonical-schema.ipynb)
[![Open in GitHub](https://img.shields.io/badge/GitHub-notebook-181717?logo=github)](https://github.com/fischer3-net/accurate_secure_rag_systems/blob/main/labs/extra-credit/notebooks/lab-ec.1-canonical-schema.ipynb)

*Run in the browser with [Google Colab](../resources/colab.md) or locally via [Docker](../resources/docker.md) / [VS Code](../resources/vscode.md).*

**Objective:** Turn the fidelity principles from the theory page into a concrete, versioned DFD schema and a validation skill that makes incompleteness visible before any policy or path evaluation runs.

---

## Learning Goals

- Extend (or harden) the existing DFD graph schema with required security-relevant properties.
- Implement a stricter `validate_dfd_syntax` (or `validate_dfd_fidelity`) skill that checks structural integrity *and* presence of critical semantic attributes.
- Demonstrate a controlled conversion pattern that preserves provenance.
- Show that the router can refuse a “full evaluation” route when validation fails.

---

## Why this lab exists

Blind export from diagramming tools routinely drops:

- Explicit trust-boundary crossings
- Data classification on stores
- Authentication / protocol attributes on flows
- Provenance (who produced the diagram, when, with which tool)

If those losses remain invisible, every downstream skill produces answers that look authoritative but rest on an incomplete model. This lab makes the losses explicit.

---

## Starter Location (suggested)

```
labs/extra-credit/
├── src/
│   ├── schema_canonical.py      # versioned DFD schema + required properties
│   ├── validate_fidelity.py     # extended validation skill
│   └── convert_with_provenance.py
├── data/
│   ├── sample_dfd_complete.json
│   ├── sample_dfd_lossy.json    # deliberately missing attributes / edges
│   └── sample_dfd_visual_notes.md
├── notebooks/
│   └── lab-ec.1-canonical-schema.ipynb
└── tests/
    └── test_fidelity_validation.py
```

You may extend the existing `labs/02-storage/src/graph_schema.py` and `labs/03-skills` validation skill instead of creating a parallel package—consistency with the main course artifacts is preferred.

---

## Step-by-Step

### 1. Define the canonical schema

Start from the Lab 2.2 schema and make the following properties required (or strongly recommended with explicit warnings) for high-risk evaluation:

| Node / Edge type   | Required or strongly recommended properties          |
|--------------------|------------------------------------------------------|
| `DataStore`        | `classification`, `trust_level`                      |
| `Process`          | `trust_level`                                        |
| `FLOWS_TO`         | `protocol`, optional `authenticated` / `encrypted`   |
| `CROSSES`          | explicit link to a `TrustBoundary`                   |
| Document root      | `source_tool`, `source_hash` or `source_uri`, `version`, `author` |

### 2. Implement fidelity-aware validation

The validation skill should return a structured result that distinguishes:

- Hard errors (broken references, missing mandatory topology)
- Soft warnings (missing semantic attributes that reduce evaluation confidence)

### 3. Controlled conversion sketch

Show a function that:

- Accepts a raw export (or the existing sample)
- Emits a `DfdDocument` plus a provenance block
- Records what was inferred versus what was explicit

### 4. Router integration

Demonstrate that the Skill Router (Lab 3.2) can refuse the `full` evaluation route when hard validation errors exist, and can attach a confidence or incompleteness flag when only soft warnings are present.

---

## Implementation Notes

Concrete starting points for the schema, validation skill, and provenance helper are provided in the [Theory – Recommended Python Building Blocks](theory.md#7-recommended-python-building-blocks) section. You can copy those dataclasses and functions into `labs/extra-credit/src/` (or extend the existing `graph_schema.py` and skills packages) and adapt them to the course’s Pydantic / registry conventions.

Key design choices to preserve:

- Distinguish **hard errors** (broken topology) from **soft warnings** (missing semantic attributes).
- Attach a `Provenance` block so every evaluated DFD carries source tool, hash, and converter version.
- Let the router refuse the `full` evaluation route when hard errors exist.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Schema documents required vs optional properties | Yes |
| Validation distinguishes hard errors from soft warnings | Yes |
| Lossy sample produces visible, structured warnings/errors | Yes |
| Router can gate the full-evaluation route on validation result | Yes |
| Unit tests cover both complete and lossy fixtures | Yes |

---

## Validation Checklist

- [ ] Canonical schema is versioned and documented
- [ ] Validation skill returns structured, machine-readable issues
- [ ] Provenance fields are present on the document
- [ ] At least one deliberately lossy fixture is included and correctly flagged
- [ ] Notebook demonstrates the difference between a complete and a lossy DFD
