.PHONY: check check-prod progress doctor bench db-up migrate dev-api dev-web

STEP ?= 1

# PostgreSQL local de `make db-up`. Codespaces y CI ya traen su propia DATABASE_URL.
DATABASE_URL ?= postgresql://postgres:postgres@localhost:5432/tiendita
export DATABASE_URL

check:
	@set -e; \
	if [ "$(STEP)" = "1" ]; then \
		uv run pytest backend/tests/step1 -v; \
	elif [ "$(STEP)" = "2" ]; then \
		uv run pytest backend/tests/step2 -v; \
	elif [ "$(STEP)" = "3" ]; then \
		uv run pytest backend/tests/step3 -v; \
	elif [ "$(STEP)" = "4" ]; then \
		uv run pytest backend/tests/step4 -v; \
	elif [ "$(STEP)" = "5" ]; then \
		(cd frontend && npm run typecheck && npm test && npm run build); \
	else \
		echo "STEP debe ser 1, 2, 3, 4 o 5."; exit 1; \
	fi

check-prod:
	@uv run pytest backend/tests/step5/test_prod_deploy.py -v

progress:
	@uv run python scripts/progress.py

doctor:
	@python3 scripts/doctor.py

bench:
	@uv run python scripts/bench_search.py

db-up:
	@docker compose up -d db

migrate:
	@uv run python db/load.py --seed

dev-api:
	@uv run uvicorn tiendita.api.app:app --app-dir backend --reload --port 8000

dev-web:
	@cd frontend && npm run dev
