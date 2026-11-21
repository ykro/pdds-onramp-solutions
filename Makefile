.PHONY: check check-prod self-check progress doctor bench migrate db-up dev-api dev-web

STEP ?= 1
EXTRA ?= 0
ARGS ?=

ifeq ($(EXTRA),1)
PYTEST_MARKER := -m "not prod"
else
PYTEST_MARKER := -m "not extra and not prod"
endif

check:
	@set -e; \
	if [ "$(STEP)" = "1" ]; then \
		uv run pytest backend/tests/step1 $(PYTEST_MARKER) -v; \
	elif [ "$(STEP)" = "2" ]; then \
		uv run pytest backend/tests/step2 $(PYTEST_MARKER) -v; \
	elif [ "$(STEP)" = "3" ]; then \
		uv run pytest backend/tests/step3 $(PYTEST_MARKER) -v; \
	elif [ "$(STEP)" = "4" ]; then \
		uv run pytest backend/tests/step4 $(PYTEST_MARKER) -v; \
	elif [ "$(STEP)" = "5" ]; then \
		(cd frontend && npx tsc --noEmit && npm test && npm run build); \
		if [ "$(EXTRA)" = "1" ]; then \
			(cd frontend && npx playwright install chromium && npx playwright test); \
		fi; \
	else \
		echo "STEP debe ser 1, 2, 3, 4 o 5."; exit 1; \
	fi

check-prod:
	@uv run pytest backend/tests/step5/test_prod_deploy.py -v

self-check:
	@if [ "$(STEP)" = "1" ]; then uv run python steps/01-terminal-git/self_check.py $(ARGS); \
	elif [ "$(STEP)" = "2" ]; then uv run python steps/02-rules-algorithms/self_check.py $(ARGS); \
	elif [ "$(STEP)" = "3" ]; then uv run python steps/03-sql/self_check.py $(ARGS); \
	elif [ "$(STEP)" = "4" ]; then uv run python steps/04-api-auth/self_check.py $(ARGS); \
	elif [ "$(STEP)" = "5" ]; then uv run python steps/05-react-deploy/self_check.py $(ARGS); \
	else echo "STEP debe ser 1, 2, 3, 4 o 5."; exit 1; fi

progress:
	@uv run python scripts/progress.py

doctor:
	@python3 scripts/doctor.py

bench:
	@uv run python scripts/bench_search.py

db-up:
	@docker compose up -d db

migrate:
	@uv run python db/load.py --up-to 2 --seed

dev-api:
	@uv run uvicorn tiendita.api.app:app --app-dir backend --reload --port 8000

dev-web:
	@cd frontend && npm run dev
