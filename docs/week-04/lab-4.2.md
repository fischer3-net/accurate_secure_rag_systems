# Lab 4.2 – Cloud Build Quality Gates with Ragas

**Objective:** Create a Cloud Build (or GitHub Actions) pipeline that, on every push, runs the Ragas evaluation suite and fails the build if Faithfulness (or other chosen metrics) falls below the defined threshold (e.g., 92%).

## Deliverables

- `cloudbuild.yaml` (or GitHub Actions workflow) that:
  1. Installs dependencies
  2. Runs `pytest` + Ragas against the golden dataset
  3. Publishes metric reports (optional: to BigQuery or Cloud Monitoring)
  4. Fails on quality-gate violation
- Documented threshold configuration that can be adjusted per environment.

## Starter Location

```
labs/04-evaluation/
cloudbuild.yaml
tests/test_ragas_metrics.py
```
