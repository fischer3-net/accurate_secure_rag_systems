# Capstone Requirements

## Functional Requirements

1. **Ingestion**  
   Ingest and store SDLC handbooks and security requirements using an optimal hybrid GCP storage pattern chosen and justified by the team.

2. **Modular Skills**  
   Implement at least three single-responsibility Python skills (Vertex AI Function Calling + Pydantic) covering:
   - Diagram syntax / structural validation
   - Security-control matching
   - SDLC gate / compliance scoring

3. **Structured Output**  
   Enforce a well-defined JSON schema for the final evaluation report (pass/fail per control, risk tier, evidence references, overall score).

4. **Automated Testing**  
   Provide a `pytest` + Ragas (or equivalent) suite that proves the system achieves >90% precision and groundedness on the golden dataset (or an extended version created by the team).

## Non-Functional Requirements

- Least-privilege IAM for all GCP resources.
- Defenses against indirect prompt injection from untrusted DFD inputs.
- Reproducible provisioning (Terraform or documented `gcloud` scripts).
- Clear README explaining architecture decisions and how to run the evaluation suite.

## Submission

- Private or public GitHub repository (or fork of the course starter).
- Link submitted via the Moodle Capstone assignment activity.
- Optional short architecture decision record (ADR) document.
