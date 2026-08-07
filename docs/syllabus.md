# Course Syllabus

**Course Title:** Advanced RAG Architecture, Custom Skills & Evaluation on Google Cloud Platform  
**Target Audience:** Security Professionals, Cloud Architects, and Python Developers  
**Prerequisites:** Proficiency in Python, basic familiarity with GCP (Vertex AI), and core understanding of LLM/RAG concepts  
**Format:** 4-Week Intensive Hands-on Workshop + Extra Credit Module + Capstone  

---

## Executive Summary & Course Goals

Organizations are increasingly leveraging Retrieval-Augmented Generation (RAG) to automate complex analytical tasks—such as evaluating **Data Flow Diagrams (DFDs)** against strict technical requirements, security baselines, diagramming standards, and internal SDLC handbooks. Moving from a basic vector search proof-of-concept to an enterprise-grade, secure, and highly accurate production system presents significant engineering challenges.

This course directly addresses the key knowledge gaps:

1. **Accuracy & Data Management** — Hybrid, chunking-aware, and structured domain retrieval.
2. **Storage Architecture Selection** — Evaluating vector stores, graph databases, and relational/hybrid options on Google Cloud Platform.
3. **Skill & Prompt Engineering** — Modular LLM “Skills” (tools/functions) without context-window bloat.
4. **Automated Evaluation & CI/CD Testing** — Continuous verification of faithfulness, relevance, context recall, and security compliance.
5. **Representation Fidelity (Extra Credit)** — Understanding what is lost when visual DFDs become structured inputs to RAG systems.

## Learning Objectives

By the end of this course, students will be able to:

- Architect hybrid RAG pipelines with custom chunking, metadata enrichment, and hybrid search (Vector + Keyword + Knowledge Graph) tailored to multi-document alignment (DFDs + Security Standards + SDLC).
- Select and provision optimal GCP storage options (Vertex AI Vector Search, pgvector on Cloud SQL / AlloyDB, BigQuery, Neo4j / Spanner Graph), including a cost-controlled student stack designed to stay under **$50 / month**.
- Develop single-responsibility agentic skills in Python (Pydantic + Vertex AI function calling) without prompt bloat or tool overload.
- Implement automated RAG evaluation pipelines using Ragas, deterministic metrics, and GitHub Actions / Cloud Build quality gates.
- (Extra Credit) Design canonical DFD schemas, validation skills, and experiments that measure the impact of fidelity loss on compliance answers.

## Course Structure at a Glance

| Module | Focus | Key Labs |
|--------|-------|----------|
| **Week 1** | Precision RAG & Domain Chunking | Lab 1.1 Document-aware chunking & metadata · Lab 1.2 Hybrid retrieval + re-ranking |
| **Week 2** | Storage Architecture on GCP | Lab 2.1 AlloyDB-style pgvector vs Vector Search · Lab 2.2 Graph-Augmented RAG |
| **Week 3** | Skill Architecture & Prompt Hygiene | Lab 3.1 Modular skills with function calling · Lab 3.2 Dynamic Skill Router |
| **Week 4** | Automated Evaluation & CI/CD | Lab 4.1 Golden dataset & Ragas · Lab 4.2 Cloud Build / GitHub Actions quality gates |
| **Extra Credit** | DFD Fidelity & RAG Implications | Lab EC.1 Canonical schema & validation · Lab EC.2 Measuring fidelity impact |
| **Capstone** | End-to-end production pipeline | Automated DFD Security & SDLC Compliance Evaluator (>90% precision & groundedness) |

---

## Detailed Weekly Modules

### Week 1 – Precision RAG & Domain Chunking

*Focus: Tackling inaccuracy, hallucination, and naive retrieval when cross-referencing DFDs with multi-source policies.*

- The multi-document alignment problem (DFDs + standards + SDLC handbooks)
- Document-aware and parent-child chunking strategies in Python
- Compliance-oriented metadata enrichment
- Hybrid retrieval: BM25 + dense vectors + Reciprocal Rank Fusion + re-ranking
- **Labs:** Lab 1.1 Document-aware chunking & metadata · Lab 1.2 Hybrid retrieval + re-ranking

### Week 2 – Storage Architecture on GCP

*Focus: Navigating storage trade-offs, vector engines, hybrid databases, and graph RAG on GCP.*

- Architectural trade-off matrix (latency, cost, filterability, operational complexity)
- AlloyDB-style hybrid SQL + vector (pgvector on Cloud SQL) vs pure semantic Vector Search
- Graph-augmented RAG over Data Flow Diagram trust boundaries
- Offline-first lab implementations with optional live GCP backends
- **Labs:** Lab 2.1 Hybrid store benchmark · Lab 2.2 Graph-Augmented RAG

### Week 3 – Skill Architecture & Prompt Hygiene

*Focus: Designing clean, single-purpose skills/tools while preventing token bloat, tool confusion, and context drift.*

- Anatomy of a skill (schema, prompt hygiene, side effects)
- Anti-pattern: the mega-prompt
- Four Pydantic skills: syntax, graph, policy, score
- SkillRegistry with Vertex AI tool declarations and a dynamic SkillRouter
- **Labs:** Lab 3.1 Modular skills with Vertex AI function calling · Lab 3.2 Dynamic Skill Router

### Week 4 – Automated Evaluation & CI/CD

*Focus: Moving from manual spot-checks to automated, continuous accuracy and compliance testing.*

- The evaluation triad: retrieval quality, answer quality, and security/compliance assertions
- Golden datasets and deterministic metrics (hit-rate, precision, groundedness)
- `eval_runner` and GitHub Actions quality gates; Cloud Build sketch
- **Labs:** Lab 4.1 Golden dataset & Ragas · Lab 4.2 Cloud Build / Actions quality gates

### Extra Credit – DFD Fidelity & RAG Implications

*Focus: What is lost (and what is gained) when visual Data Flow Diagrams are converted into structured JSON/graph representations for RAG-based evaluation.*

- Taxonomy of fidelity loss: visual, structural, semantic, provenance
- How incompleteness propagates into retrieval, path queries, skills, and evaluation metrics
- Canonical schema design and validation skills that surface missing security-relevant information
- Controlled experiments measuring impact on compliance answers
- **Labs:** Lab EC.1 Canonical schema & validation · Lab EC.2 Measuring fidelity impact

---

## Capstone Project

### Automated DFD Security & SDLC Compliance Evaluator

Students implement an end-to-end production-style pipeline that:

1. **Ingests** a structured representation (JSON / graph) of a Data Flow Diagram together with SDLC and security baseline documents.
2. **Retrieves** relevant controls and handbook sections using the hybrid + graph patterns from Weeks 1–2.
3. **Applies modular skills** (syntax, graph/path, policy, scoring) from Week 3.
4. **Emits structured JSON** detailing pass/fail controls, risk notes, and source references.
5. **Passes an automated quality gate** (`pytest` + deterministic metrics / Ragas) demonstrating **>90% precision and groundedness**.

Starter mapping of Weeks 1–4 artefacts is provided under the Capstone section of the site and in the repository.

---

## Environments & Infrastructure

| Environment | Purpose | Entry point |
|-------------|---------|-------------|
| **Docker + JupyterLab** | Primary offline lab runtime (Python 3.11) | `./scripts/setup_local.sh` or `make setup-local` |
| **VS Code Dev Containers** | Full IDE inside the same image | See [VS Code guide](resources/vscode.md) |
| **Google Colab** | Zero local install experiments | [Colab guide](resources/colab.md) |
| **Live GCP (Terraform)** | Optional Cloud SQL + pgvector, GCS, Vertex AI SA (≤ **$50 / mo**) | `./scripts/setup_gcp.sh` / `make setup-gcp` |
| **MkDocs only** | Preview the course site | `make docs-serve` |

Full comparison and setup steps: **[Testing Environments](resources/environments.md)**.

Teardown GCP resources when finished: `./scripts/teardown_gcp.sh` or `make teardown-gcp`.

---

## Recommended Tooling & Stack

| Layer | Technology |
|:------|:-----------|
| **Language & Runtime** | Python 3.11+, Docker / JupyterLab |
| **LLM & Embeddings** | Vertex AI Gemini, `text-embedding-004` (and compatible embedding models) |
| **Vector & Hybrid Storage** | Cloud SQL PostgreSQL + pgvector (student default), Vertex AI Vector Search (optional), AlloyDB (advanced) |
| **Graph Storage** | In-lab graph store; Neo4j / Spanner Graph as optional live backends |
| **Skills / Tools** | Pydantic models, Vertex AI function calling / tool declarations |
| **Evaluation** | Deterministic metrics, Ragas, `pytest`, GitHub Actions quality gates |
| **CI/CD & DevOps** | GitHub Actions, Cloud Build sketch, Secret Manager, Artifact Registry |
| **IaC (optional live)** | Terraform package under `terraform/` (cost-controlled) |

---

## Assessment Summary

| Component | Weight / expectation |
|-----------|----------------------|
| Weekly labs (1.1–4.2) | Completion + unit tests where provided |
| Extra Credit labs (EC.1–EC.2) | Optional; strongly recommended before Capstone |
| Capstone | Working pipeline + automated suite meeting **>90%** precision and groundedness gate |

---

## How to Navigate This Site

- Use the **left sidebar** for the full course tree (Weeks 1–4, Extra Credit, Capstone, Resources).
- Each week contains an **Overview**, **Theory**, and hands-on **Lab** pages.
- Lab source, tests, and notebooks live in the repository under `labs/` and `notebooks/`.
- Start with [Week 1 – Overview](week-01/index.md) or review [Testing Environments](resources/environments.md) if you are setting up your machine.
