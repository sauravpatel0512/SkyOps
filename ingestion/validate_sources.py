"""Validate that required local source files exist before load."""

from __future__ import annotations

import os
from pathlib import Path

from ingestion.download_bts import csv_ready
from ingestion.load_weather import weather_json_path


def validate_sources(year: int | None = None) -> None:
    year = year or int(os.environ.get("SKYOPS_YEAR", "2024"))
    months = [m for m in range(1, 13) if csv_ready(year, m)]
    if not months:
        raise FileNotFoundError(
            f"No BTS monthly zips for {year} under data/raw/bts/. Run: make download-bts"
        )
    wpath = weather_json_path(year)
    # Weather may be fetched later in the DAG; warn only if force_weather=1
    if os.environ.get("SKYOPS_REQUIRE_WEATHER") == "1" and not wpath.exists():
        raise FileNotFoundError(f"Missing {wpath}")
    print(f"validate_sources ok: year={year} bts_months={months}")


def repo_has_fixture() -> bool:
    root = Path(__file__).resolve().parents[1]
    return (root / "data" / "fixtures" / "flights_sample.csv").exists()


if __name__ == "__main__":
    validate_sources()
