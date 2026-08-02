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
    JUPYTER_PORT=8888 \
    COURSE_HOME=/home/fischer3/course \
    HOME=/home/fischer3 \
    JUPYTER_CONFIG_DIR=/home/fischer3/.jupyter \
    JUPYTER_DATA_DIR=/home/fischer3/.local/share/jupyter \
    JUPYTER_RUNTIME_DIR=/home/fischer3/.local/share/jupyter/runtime

# System packages (gosu drops privileges after fixing volume ownership)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        tini \
        gosu \
    && rm -rf /var/lib/apt/lists/*

# Course user (replaces the generic Jupyter "jovyan" convention)
RUN useradd -m -u 1000 -s /bin/bash fischer3 \
    && mkdir -p \
        "${COURSE_HOME}" \
        /home/fischer3/.jupyter \
        /home/fischer3/.local/share/jupyter/runtime \
    && chown -R fischer3:fischer3 /home/fischer3

WORKDIR ${COURSE_HOME}

COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY docker/entrypoint.sh /usr/local/bin/course-entrypoint.sh
RUN chmod +x /usr/local/bin/course-entrypoint.sh

# Remain root so entrypoint can chown named volumes, then gosu → fischer3
EXPOSE 8888

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/course-entrypoint.sh"]
CMD ["jupyter", "lab"]
