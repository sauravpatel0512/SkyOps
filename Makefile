.PHONY: help up down init-db download download-bts download-weather load lint test ci-local open-dashboard psql logs dbt-dev dbt-cloud dbt-freshness

help:
	@echo "SkyOps targets:"
	@echo "  download          BTS 2024 months + Open-Meteo hub weather"
	@echo "  download-bts      BTS monthly PREZIP only"
	@echo "  download-weather  Open-Meteo daily weather for hubs"
	@echo "  load              load weather + flights into Postgres"
	@echo "  up                docker compose up -d --build"
	@echo "  down              docker compose down"
	@echo "  init-db           apply sql/*.sql into skyops-postgres"
	@echo "  dbt-dev           dbt build --target dev (local Postgres)"
	@echo "  dbt-cloud         dbt build --target cloud (Neon/RDS; needs CLOUD_POSTGRES_*)"
	@echo "  dbt-freshness     dbt source freshness on raw.flights / raw.weather_daily"
	@echo "  lint              ruff check"
	@echo "  test              pytest"
	@echo "  ci-local          install deps + lint + test"
	@echo "  open-dashboard    print Airflow / Metabase URLs"
	@echo "  psql              psql shell"
	@echo "  logs              compose logs"

download: download-bts download-weather

download-bts:
	python -m ingestion.download_bts

download-weather:
	python -m ingestion.fetch_weather

load:
	python -m ingestion.load_weather
	python -m ingestion.load_flights

up:
	docker compose up -d --build

down:
	docker compose down

init-db:
	docker exec -i skyops-postgres psql -U postgres -d skyops -f - < sql/init.sql
	docker exec -i skyops-postgres psql -U postgres -d skyops -f - < sql/raw_schema.sql
	docker exec -i skyops-postgres psql -U postgres -d skyops -f - < sql/analytics_schema.sql

# Host-side dbt against local published Postgres (port 5433 by default).
dbt-dev:
	cd dbt && POSTGRES_HOST=$${POSTGRES_HOST:-localhost} POSTGRES_PORT=$${POSTGRES_PORT:-5433} POSTGRES_SSLMODE=$${POSTGRES_SSLMODE:-disable} \
		dbt deps --profiles-dir . && \
		dbt seed --profiles-dir . --target dev && \
		dbt build --profiles-dir . --target dev

# Managed Postgres (Neon / RDS). Export CLOUD_POSTGRES_* first — see .env.example.
dbt-cloud:
	@test -n "$${CLOUD_POSTGRES_HOST}" || (echo "Set CLOUD_POSTGRES_HOST (and user/password). See .env.example" >&2; exit 1)
	cd dbt && dbt deps --profiles-dir . && \
		dbt seed --profiles-dir . --target cloud && \
		dbt build --profiles-dir . --target cloud

# Fails if raw.flights / raw.weather_daily were not ingested in the last 7 days.
dbt-freshness:
	cd dbt && POSTGRES_HOST=$${POSTGRES_HOST:-localhost} POSTGRES_PORT=$${POSTGRES_PORT:-5433} POSTGRES_SSLMODE=$${POSTGRES_SSLMODE:-disable} \
		dbt source freshness --profiles-dir . --target $${DBT_TARGET:-dev}

lint:
	ruff check ingestion airflow/dags airflow/plugins tests

test:
	pytest tests/ -q

ci-local:
	python -m pip install -r requirements.txt
	$(MAKE) lint
	$(MAKE) test

open-dashboard:
	@echo Open http://localhost:8080 (Airflow) and http://localhost:3000 (Metabase)

psql:
	docker exec -it skyops-postgres psql -U postgres -d skyops

logs:
	docker compose logs -f --tail=200
