# Student Jupyter environment for
# Advanced RAG Architecture, Custom Skills & Evaluation on GCP
#
# Build:  docker compose build
# Run:    docker compose up
# Open:   http://localhost:8888

FROM python:3.11-slim-bookworm

LABEL org.opencontainers.image.title="accurate-secure-rag-systems"
LABEL org.opencontainers.image.description="JupyterLab environment for the Advanced RAG course"
LABEL org.opencontainers.image.source="https://github.com/fischer3-net/accurate_secure_rag_systems"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Jupyter
    JUPYTER_PORT=8888 \
    # Course materials live here inside the container
    COURSE_HOME=/home/jovyan/course \
    HOME=/home/jovyan

# System packages: build tools for any wheels, curl for healthchecks, git for student forks
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Non-root user (matches common Jupyter images)
RUN useradd -m -u 1000 -s /bin/bash jovyan \
    && mkdir -p "${COURSE_HOME}" \
    && chown -R jovyan:jovyan /home/jovyan

WORKDIR ${COURSE_HOME}

# Install Python dependencies as root, then drop privileges
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Lightweight entrypoint: start JupyterLab without a token for local workshops.
# Override JUPYTER_TOKEN in compose or environment for shared / cloud hosts.
COPY docker/entrypoint.sh /usr/local/bin/course-entrypoint.sh
RUN chmod +x /usr/local/bin/course-entrypoint.sh

USER jovyan

EXPOSE 8888

# tini reaps zombies from notebook kernels
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/course-entrypoint.sh"]
