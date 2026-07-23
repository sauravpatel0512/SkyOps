# SkyOps — End-to-end runbook

Assumes repo root and Docker Desktop running.

## One full pass

```bash
cp .env.example .env
pip install -r requirements.txt
make download                 # BTS 2024 months + Open-Meteo hubs
docker compose up -d --build
# wait for Airflow http://localhost:8080
make init-db                 # if volumes already existed
docker exec skyops-airflow-webserver airflow dags trigger skyops_daily
```

Expected: DAG green; `analytics.mart_*` populated; Metabase at http://localhost:3000.

## Offline / manual BTS

If PREZIP downloads fail (HTTP 403), download monthly On-Time zips from TranStats and save as:

`data/raw/bts/bts_ontime_2024_01.zip` … `_12.zip`

Then re-run `make download-weather` and trigger the DAG (download task will skip existing files).

## Local dbt without Airflow

```bash
# with Postgres up and raw loaded
cd dbt
set POSTGRES_HOST=localhost
dbt deps --profiles-dir .
dbt seed --profiles-dir .
dbt build --profiles-dir .
```

## CI path

GitHub Actions loads `data/fixtures/flights_sample.csv` instead of full BTS.
