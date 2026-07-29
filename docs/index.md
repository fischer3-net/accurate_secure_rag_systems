# Advanced RAG Architecture, Custom Skills & Evaluation on Google Cloud Platform

**Target Audience:** Security Professionals, Cloud Architects, and Python Developers  
**Prerequisites:** Proficiency in Python, basic familiarity with GCP (Vertex AI), and core understanding of LLM/RAG concepts  
**Format:** 4-Week Intensive / Hands-on Workshop Style  

---

## Executive Summary

Organizations are increasingly leveraging Retrieval-Augmented Generation (RAG) to automate complex analytical tasks—such as evaluating **Data Flow Diagrams (DFDs)** against strict technical requirements, security baselines, diagramming standards, and internal SDLC handbooks. Moving from a basic vector search proof-of-concept to an enterprise-grade, secure, and highly accurate production system presents significant engineering challenges.

This course directly addresses the key knowledge gaps:

1. **Accuracy & Data Management** — Hybrid, chunking-aware, and structured domain retrieval.
2. **Storage Architecture Selection** — Evaluating vector stores, graph databases, and relational/hybrid options on Google Cloud Platform.
3. **Skill & Prompt Engineering** — Modular LLM “Skills” (tools/functions) without context-window bloat.
4. **Automated Evaluation & CI/CD Testing** — Continuous verification of faithfulness, relevance, context recall, and security compliance.

## Learning Objectives

By the end of this course you will be able to:

- Architect hybrid RAG pipelines with custom chunking, metadata enrichment, and hybrid search (Vector + Keyword + Knowledge Graph) tailored to multi-document alignment (DFDs + Security Standards + SDLC).
- Select and provision optimal GCP storage options (Vertex AI Vector Search, pgvector on Cloud SQL / AlloyDB, BigQuery, Neo4j / Spanner Graph).
- Develop single-responsibility agentic skills in Python without prompt bloat or tool overload.
- Implement automated RAG evaluation pipelines using Ragas, Vertex AI Evaluation, and deterministic assertions, integrated into Cloud Build / GitHub Actions quality gates.

## Course Structure at a Glance

| Week | Focus | Key Labs |
|------|-------|----------|
| 1 | Precision RAG & Domain Chunking | Document-aware chunking, Hybrid retrieval + re-ranking |
| 2 | Storage Architecture on GCP | AlloyDB pgvector vs Vertex AI Vector Search, Graph RAG |
| 3 | Skill Architecture & Prompt Hygiene | Modular Function Calling, Dynamic Skill Router |
| 4 | Automated Evaluation & CI/CD | Golden datasets + Ragas, Cloud Build quality gates |
| Capstone | Automated DFD Security & SDLC Compliance Evaluator | End-to-end production pipeline |

## How to Use This Site

- Navigate via the top tabs or left sidebar.
- Each week contains an **Overview**, detailed **Theory**, and hands-on **Lab** pages.
- Lab code and notebooks live in the repository under `/labs` and `/notebooks`.
- The Capstone section contains the full project specification and starter template guidance.

Ready to begin? Start with the [Syllabus](syllabus.md) or jump straight into [Week 1](week-01/index.md).
