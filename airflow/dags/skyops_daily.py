"""SkyOps batch DAG: download BTS → validate → load flights → weather → dbt build."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingestion.download_bts import csv_ready, download_year
from ingestion.load_flights import run_load
from ingestion.load_weather import run_fetch
from ingestion.validate_sources import validate_sources

default_args = {
    "owner": "skyops",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


def _year() -> int:
    return int(os.environ.get("SKYOPS_YEAR", "2024"))


def _download() -> None:
    year = _year()
    try:
        download_year(year)
    except Exception as exc:
        if not any(csv_ready(year, m) for m in range(1, 13)):
            raise exc
        print(f"download partial/failed, continuing with cached files: {exc}")


def _validate() -> None:
    validate_sources(_year())


def _load_flights() -> None:
    run_load(_year())


def _weather() -> None:
    run_fetch(_year())


with DAG(
    dag_id="skyops_daily",
    description="BTS flights + Open-Meteo weather ingest, then dbt build.",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["skyops"],
) as dag:
    download_bts_task = PythonOperator(
        task_id="download_bts",
        python_callable=_download,
    )
    validate_sources_task = PythonOperator(
        task_id="validate_sources",
        python_callable=_validate,
    )
    load_flights_task = PythonOperator(
        task_id="load_raw_flights",
        python_callable=_load_flights,
    )
    fetch_weather_task = PythonOperator(
        task_id="fetch_weather",
        python_callable=_weather,
    )
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt deps --profiles-dir . && "
            "dbt source freshness --profiles-dir . && "
            "dbt seed --profiles-dir . && "
            "dbt build --profiles-dir ."
        ),
        env={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "skyops",
        },
    )

    (
        download_bts_task
        >> validate_sources_task
        >> load_flights_task
        >> fetch_weather_task
        >> dbt_build
    )
