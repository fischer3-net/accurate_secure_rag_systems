#!/usr/bin/env bash
# Fix volume permissions (named volumes start as root), then run as fischer3.
set -euo pipefail

COURSE_HOME="${COURSE_HOME:-/home/fischer3/course}"
USER_NAME="${COURSE_USER:-fischer3}"

# Ensure Jupyter dirs exist and are writable by the course user.
# Named Docker volumes are root-owned on first create — that caused:
#   PermissionError: ... '/home/.../.jupyter/migrated'
if [[ "$(id -u)" -eq 0 ]]; then
  mkdir -p \
    /home/"${USER_NAME}"/.jupyter \
    /home/"${USER_NAME}"/.local/share/jupyter/runtime \
    /home/"${USER_NAME}"/.local/share/jupyter
  chown -R "${USER_NAME}:${USER_NAME}" \
    /home/"${USER_NAME}"/.jupyter \
    /home/"${USER_NAME}"/.local || true
  # Drop privileges and re-exec this script as fischer3
  exec gosu "${USER_NAME}" "$0" "$@"
fi

cd "${COURSE_HOME}"

# Register a friendly kernel name (ignore failures on re-run)
python -m ipykernel install --user \
  --name=rag-course \
  --display-name="RAG Course (Python 3.11)" 2>/dev/null || true

TOKEN_ARGS=()
if [[ -n "${JUPYTER_TOKEN:-}" ]]; then
  TOKEN_ARGS+=(--ServerApp.token="${JUPYTER_TOKEN}")
  TOKEN_ARGS+=(--ServerApp.password='')
else
  # Local workshop default: no token
  TOKEN_ARGS+=(--ServerApp.token='')
  TOKEN_ARGS+=(--ServerApp.password='')
fi

echo "============================================================"
echo " Advanced RAG – JupyterLab"
echo " User:        ${USER_NAME}"
echo " Course root: ${COURSE_HOME}"
echo " Labs:        ${COURSE_HOME}/labs/"
echo " Open:        http://localhost:${JUPYTER_PORT:-8888}"
if [[ -n "${JUPYTER_TOKEN:-}" ]]; then
  echo " Token:       ${JUPYTER_TOKEN}"
else
  echo " Token:       (none – local use only)"
fi
echo "============================================================"

# If CMD was provided (default: jupyter lab), run it; otherwise start lab.
if [[ $# -gt 0 && "$1" != "jupyter" ]]; then
  exec "$@"
fi

# Default / explicit jupyter lab launch
if [[ $# -eq 0 || "$1" == "jupyter" ]]; then
  shift $(( $# > 0 ? 1 : 0 )) || true
  if [[ $# -gt 0 && "$1" == "lab" ]]; then
    shift
  fi
  exec jupyter lab \
    --ip=0.0.0.0 \
    --port="${JUPYTER_PORT:-8888}" \
    --no-browser \
    --ServerApp.root_dir="${COURSE_HOME}" \
    --ServerApp.allow_origin='*' \
    --ServerApp.authenticate_prometheus=False \
    "${TOKEN_ARGS[@]}" \
    "$@"
fi

exec "$@"
