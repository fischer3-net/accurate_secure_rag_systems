# Course Syllabus

**Course Title:** Advanced RAG Architecture, Custom Skills & Evaluation on Google Cloud Platform  
**Target Audience:** Security Professionals, Cloud Architects, and Python Developers  
**Prerequisites:** Proficiency in Python, basic familiarity with GCP (Vertex AI), and core understanding of LLM/RAG concepts  
**Format:** 4-Week Intensive / Hands-on Workshop Style  

---

## Executive Summary & Course Goals

Organizations are increasingly leveraging Retrieval-Augmented Generation (RAG) to automate complex analytical tasks—such as evaluating **Data Flow Diagrams (DFDs)** against strict technical requirements, security baselines, diagramming standards, and internal SDLC handbooks. However, moving from a basic vector search proof-of-concept to an enterprise-grade, secure, and highly accurate production system presents significant engineering challenges.

This course directly addresses key knowledge gaps in building production RAG systems:

1. **Accuracy & Data Management:** Moving beyond naive semantic search to hybrid, chunking-aware, and structured domain retrieval.
2. **Storage Architecture Selection:** Evaluating vector stores, graph databases, and relational/hybrid storage options on Google Cloud Platform (GCP).
3. **Skill & Prompt Engineering (Mitigating Bloat):** Structuring modular LLM "Skills" (tools/functions) and preventing context window overload.
4. **Automated Evaluation & CI/CD Testing:** Designing automated accuracy, retrieval, and safety test suites for continuous verification.

## Learning Objectives

By the end of this course, students will be able to:

- **Architect Hybrid RAG Pipelines:** Implement custom chunking, metadata enrichment, and hybrid search (Vector + Keyword + Knowledge Graph) tailored to multi-document alignment (DFDs + Security Standards + SDLC).
- **Select & Provision GCP Storage:** Compare and deploy optimal GCP storage options (**Vertex AI Vector Search**, **pgvector on Cloud SQL**, **AlloyDB**, and **Neo4j/Spanner Graph**) based on data structure and latency/accuracy requirements.
- **Develop Modular Skills (Tools):** Build single-responsibility agentic skills in Python without prompt bloat or tool overloading.
- **Implement Automated RAG Evaluation:** Build CI/CD evaluation pipelines using **Ragas**, **Vertex AI Evaluation Framework**, and custom deterministic assertions to benchmark Faithfulness, Answer Relevance, Context Recall, and Security Compliance.

## Detailed Weekly Modules

### Module 1: Precision RAG Management & Domain Chunking for Compliance Data
*Focus: Tackling inaccuracy, hallucination, and naive retrieval limitations when cross-referencing DFDs with multi-source policies.*

- The Multi-Document Alignment Problem
- Advanced Chunking Strategies in Python
- Hybrid Retrieval Architecture
- **Labs:** Parsing & metadata enrichment; Custom re-ranker pipeline

### Module 2: Storage Architecture & Selection on Google Cloud Platform
*Focus: Navigating storage trade-offs, vector engines, hybrid databases, and graph RAG on GCP.*

- Deconstructing RAG Storage Options on GCP
- Architectural Trade-off Matrix
- **Labs:** AlloyDB pgvector vs Vertex AI Vector Search benchmarking; Graph-Augmented RAG

### Module 3: Skill Architecture, Tooling & Curing Prompt/Skill Bloat
*Focus: Designing clean, single-purpose skills/tools in Python while preventing token bloat, tool confusion, and context drift.*

- Anatomy of a Skill in RAG Systems
- Defeating Skill and Prompt Bloat
- Security & Prompt Injection Defenses
- **Labs:** Refactoring mega-prompts into modular skills; Dynamic Skill Router

### Module 4: Automated Accuracy Testing, Evaluation Metrics & Continuous Integration
*Focus: Moving from manual spot-checks to automated, continuous accuracy, security, and performance testing pipelines.*

- The RAG Evaluation Triad & Metrics
- Building an Automated Evaluation Suite
- CI/CD Pipeline Integration
- **Labs:** Golden dataset construction; Cloud Build + Ragas quality gates

## Course Assessment & Final Capstone Project

### Capstone Project: Automated DFD Security & SDLC Compliance Evaluator

Students will work in teams or individually to build a complete, production-ready pipeline on GCP using Python:

1. **Input:** A structured Representation (JSON/XML/Mermaid) of a Data Flow Diagram.
2. **System Requirements:**
   - Ingest and store SDLC handbooks and security requirements using an optimal hybrid GCP storage pattern.
   - Implement modular Python skills for syntax checking, security matching, and compliance scoring.
   - Enforce structured JSON output detailing pass/fail controls, vulnerability risks, and references.
3. **Automated Testing:** Provide an automated test suite (`pytest` + `ragas`) proving the system achieves >90% precision and groundedness.

## Recommended Tooling & Stack Summary

| Layer | Technology / GCP Product |
| :--- | :--- |
| **Language & Runtime** | Python 3.11+, Asyncio |
| **LLM & Embeddings** | Vertex AI Gemini 1.5 Pro / Flash, `text-embedding-004` |
| **Vector & Hybrid Storage** | Vertex AI Vector Search, AlloyDB (`pgvector`), BigQuery |
| **Graph Storage (Optional)** | Neo4j on GCP / Cloud Spanner Graph |
| **Frameworks** | LangChain / LlamaIndex / Vertex AI SDK, Pydantic |
| **Evaluation Frameworks** | Ragas, Vertex AI Evaluation SDK, `pytest` |
| **CI/CD & DevOps** | GCP Cloud Build, Artifact Registry, Secret Manager |
