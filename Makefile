.PHONY: help up down init-db download download-bts download-weather lint test ci-local open-dashboard psql logs

help:
	@echo "SkyOps targets:"
	@echo "  download          BTS 2024 months + Open-Meteo hub weather"
	@echo "  download-bts      BTS monthly PREZIP only"
	@echo "  download-weather  Open-Meteo daily weather for hubs"
	@echo "  up                docker compose up -d --build"
	@echo "  down              docker compose down"
	@echo "  init-db           apply sql/*.sql into skyops-postgres"
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
