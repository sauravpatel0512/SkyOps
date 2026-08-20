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
# with Postgres up and raw loaded (host → published port 5433)
cd dbt
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5433
set POSTGRES_SSLMODE=disable
dbt deps --profiles-dir .
dbt seed --profiles-dir . --target dev
dbt build --profiles-dir . --target dev
```

Or: `make dbt-dev` from the repo root.

Check that ingest actually landed recently (`loaded_at`, not BTS `fl_date`):

```bash
make dbt-freshness
```

A warehouse that has not been re-ingested in 7 days is expected to fail. CI fixture loads with `now()` so freshness passes on GitHub Actions.

## Cloud Postgres target (Neon / RDS / Cloud SQL)

Same dbt project, separate profile output — proves env separation without changing models.

1. Create a managed Postgres instance (Neon free tier is enough for a **fixture/smoke** load).
2. Create database `skyops` (or set `CLOUD_POSTGRES_DB`).
3. Apply DDL once (from a machine that can reach the host):

   ```bash
   # example: psql with SSL
   psql "host=$CLOUD_POSTGRES_HOST user=$CLOUD_POSTGRES_USER dbname=$CLOUD_POSTGRES_DB sslmode=require" \
     -f sql/init.sql -f sql/raw_schema.sql -f sql/analytics_schema.sql
   ```

4. Put credentials in `.env` (never commit):

   ```bash
   CLOUD_POSTGRES_HOST=ep-xxxx.region.aws.neon.tech
   CLOUD_POSTGRES_PORT=5432
   CLOUD_POSTGRES_USER=...
   CLOUD_POSTGRES_PASSWORD=...
   CLOUD_POSTGRES_DB=skyops
   CLOUD_POSTGRES_SSLMODE=require
   ```

5. Load a **small** sample (CI fixture or one BTS month), then:

   ```bash
   # optional: point loaders at cloud
   # POSTGRES_HOST=... POSTGRES_SSLMODE=require python -m ingestion.load_flights
   make dbt-cloud
   ```

**Do not** push the full **7.08M**-row local warehouse to a free tier by default — quota and time. CI stays on `--target ci` with the fixture.

`ingestion.db.cloud_warehouse_dsn()` builds the same SSL DSN shape for Python loaders when `CLOUD_POSTGRES_*` is set.

## Load audit (`raw.ingestion_runs`)

After ingest, confirm what landed:

```bash
make psql
# then:
SELECT source_name, finished_at, status, row_count, notes
FROM raw.ingestion_runs
ORDER BY finished_at DESC
LIMIT 10;

SELECT * FROM staging.stg_ingestion_runs ORDER BY finished_at DESC;
```

## CI path

GitHub Actions loads `data/fixtures/flights_sample.csv` instead of full BTS.