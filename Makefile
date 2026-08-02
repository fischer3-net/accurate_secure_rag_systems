# Convenience targets for instructors and students
.PHONY: jupyter jupyter-down jupyter-rebuild docs-serve test-labs help

help:
	@echo "Targets:"
	@echo "  make jupyter          - build & start JupyterLab (http://localhost:8888)"
	@echo "  make jupyter-down     - stop the Jupyter container"
	@echo "  make jupyter-rebuild  - rebuild image without cache"
	@echo "  make docs-serve       - local MkDocs preview"
	@echo "  make test-labs        - run pytest across labs 01–04"

jupyter:
	docker compose up --build

jupyter-down:
	docker compose down

jupyter-rebuild:
	docker compose build --no-cache
	docker compose up

docs-serve:
	pip install -q -r requirements-docs.txt
	mkdocs serve

test-labs:
	@for d in labs/01-chunking labs/02-storage labs/03-skills labs/04-evaluation; do \
	  echo "=== $$d ==="; \
	  (cd $$d && python -m pytest tests/ -q --tb=line) || exit 1; \
	done
	@echo "All lab test suites passed."
