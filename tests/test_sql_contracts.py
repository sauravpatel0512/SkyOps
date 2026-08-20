"""Lightweight SQL contract checks on fixture schema names."""

from __future__ import annotations

from pathlib import Path


def test_raw_schema_defines_flights():
    sql = (Path(__file__).resolve().parents[1] / "sql" / "raw_schema.sql").read_text(encoding="utf-8")
    assert "raw.flights" in sql
    assert "raw.weather_daily" in sql
    assert "raw.airports" in sql
    assert "raw.ingestion_runs" in sql


def test_sources_yml_declares_ingestion_runs():
    yml = (Path(__file__).resolve().parents[1] / "dbt" / "models" / "sources.yml").read_text(
        encoding="utf-8"
    )
    assert "ingestion_runs" in yml


def test_stg_ingestion_runs_model_exists():
    path = Path(__file__).resolve().parents[1] / "dbt" / "models" / "staging" / "stg_ingestion_runs.sql"
    assert path.exists()
    sql = path.read_text(encoding="utf-8")
    assert "ingestion_runs" in sql


def test_sources_yml_declares_loaded_at_freshness():
    yml = (Path(__file__).resolve().parents[1] / "dbt" / "models" / "sources.yml").read_text(
        encoding="utf-8"
    )
    assert "loaded_at_field: loaded_at" in yml
    assert "warn_after" in yml
    assert "error_after" in yml
    assert "flights" in yml
    assert "weather_daily" in yml


def test_fixture_csv_exists():
    path = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "flights_sample.csv"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 5
