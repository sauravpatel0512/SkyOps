"""Lightweight SQL contract checks on fixture schema names."""

from __future__ import annotations

from pathlib import Path


def test_raw_schema_defines_flights():
    sql = (Path(__file__).resolve().parents[1] / "sql" / "raw_schema.sql").read_text(encoding="utf-8")
    assert "raw.flights" in sql
    assert "raw.weather_daily" in sql
    assert "raw.airports" in sql


def test_fixture_csv_exists():
    path = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "flights_sample.csv"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 5
