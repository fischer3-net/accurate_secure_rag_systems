#!/usr/bin/env bash
# Launch JupyterLab against the course tree.
set -euo pipefail

COURSE_HOME="${COURSE_HOME:-/home/jovyan/course}"
cd "${COURSE_HOME}"

# Optional: register a kernel display name
python -m ipykernel install --user --name=rag-course --display-name="RAG Course (Python 3.11)" 2>/dev/null || true

TOKEN_ARGS=()
if [[ -n "${JUPYTER_TOKEN:-}" ]]; then
  TOKEN_ARGS+=(--ServerApp.token="${JUPYTER_TOKEN}")
  TOKEN_ARGS+=(--ServerApp.password='')
else
  # Local workshop default: no token (bind to localhost via compose port mapping)
  TOKEN_ARGS+=(--ServerApp.token='')
  TOKEN_ARGS+=(--ServerApp.password='')
fi

echo "============================================================"
echo " Advanced RAG – JupyterLab"
echo " Course root: ${COURSE_HOME}"
echo " Labs:        ${COURSE_HOME}/labs/"
echo " Open:        http://localhost:${JUPYTER_PORT:-8888}"
if [[ -n "${JUPYTER_TOKEN:-}" ]]; then
  echo " Token:       ${JUPYTER_TOKEN}"
else
  echo " Token:       (none – local use only)"
fi
echo "============================================================"

exec jupyter lab \
  --ip=0.0.0.0 \
  --port="${JUPYTER_PORT:-8888}" \
  --no-browser \
  --ServerApp.root_dir="${COURSE_HOME}" \
  --ServerApp.allow_origin='*' \
  --ServerApp.authenticate_prometheus=False \
  "${TOKEN_ARGS[@]}" \
  "$@"
