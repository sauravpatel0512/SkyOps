"""Fetch daily weather for hub airports via Open-Meteo Historical API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

from ingestion.hubs import HUB_AIRPORTS

OPEN_METEO = "https://archive-api.open-meteo.com/v1/archive"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def weather_dir() -> Path:
    path = repo_root() / "data" / "raw" / "weather"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fetch_airport(
    iata: str,
    lat: float,
    lon: float,
    start: str,
    end: str,
) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code",
        "timezone": "America/New_York",
    }
    resp = requests.get(OPEN_METEO, params=params, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    payload["airport_iata"] = iata
    return payload


def fetch_all(year: int) -> Path:
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    out = weather_dir() / f"hubs_daily_{year}.json"
    if out.exists() and out.stat().st_size > 1000:
        print(f"skip existing {out.name}")
        return out

    results = []
    for iata, _name, _city, _state, lat, lon in HUB_AIRPORTS:
        print(f"weather {iata}")
        results.append(fetch_airport(iata, lat, lon, start, end))

    out.write_text(json.dumps(results), encoding="utf-8")
    print(f"wrote {out}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=int(os.environ.get("SKYOPS_YEAR", "2024")))
    args = parser.parse_args(argv)
    fetch_all(args.year)
    return 0


if __name__ == "__main__":
    # Allow `python -m ingestion.fetch_weather` and plain script from repo root
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.exit(main())
