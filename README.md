# Advanced RAG Architecture, Custom Skills & Evaluation on Google Cloud Platform

**Target Audience:** Security Professionals, Cloud Architects, and Python Developers  
**Prerequisites:** Proficiency in Python, basic familiarity with GCP (Vertex AI), and core understanding of LLM/RAG concepts  
**Format:** 4-Week Intensive / Hands-on Workshop Style  

---

## Course Site

The full course materials are published via GitHub Pages (Material for MkDocs):

**https://fischer3-net.github.io/accurate_secure_rag_systems/**

---

## Repository Structure

```
accurate_secure_rag_systems/
├── docs/                     # MkDocs source (theory, lab guides, syllabus)
│   ├── week-01/ ... week-04/
│   ├── capstone/
│   └── resources/
├── labs/                     # Python lab code & starter projects
├── notebooks/                # Colab / Vertex AI Workbench notebooks
├── scripts/                  # GCP provisioning helpers
├── mkdocs.yml
└── .github/workflows/ci.yml  # Auto-deploy to GitHub Pages
```

## Local Development

```bash
# Install dependencies
pip install mkdocs-material

# Serve locally
mkdocs serve

# Build
mkdocs build
```


## Student Jupyter Environment (Docker)

Run all lab notebooks in a consistent Python 3.11 stack without local package installs:

```bash
docker compose up --build
# open http://localhost:8888
```

See [docs/resources/docker.md](docs/resources/docker.md) for tokens, GCP credentials, and troubleshooting.

## Moodle Integration

This repository is the single source of truth for all instructional content.  
In Moodle:

1. Create weekly sections matching the four modules.
2. Link each section to the corresponding pages on the GitHub Pages site.
3. Use Moodle only for enrollment, quizzes, assignment submission, forums, and progress tracking.

## Capstone

Students fork or clone the starter template under `labs/` / `capstone` and implement an Automated DFD Security & SDLC Compliance Evaluator that meets the >90% precision and groundedness quality gate.

## License

Course materials © 2026. Code samples are provided under Apache 2.0 unless otherwise noted.
