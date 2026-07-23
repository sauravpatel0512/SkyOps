"""Load Open-Meteo JSON + hub airports into raw tables."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ingestion.db import warehouse_conn
from ingestion.hubs import HUB_AIRPORTS


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def weather_json_path(year: int) -> Path:
    return repo_root() / "data" / "raw" / "weather" / f"hubs_daily_{year}.json"


def upsert_airports() -> int:
    with warehouse_conn() as conn:
        with conn.cursor() as cur:
            for iata, name, city, state, lat, lon in HUB_AIRPORTS:
                cur.execute(
                    """
                    INSERT INTO raw.airports (iata_code, airport_name, city, state, latitude, longitude, is_hub)
                    VALUES (%s, %s, %s, %s, %s, %s, true)
                    ON CONFLICT (iata_code) DO UPDATE SET
                        airport_name = EXCLUDED.airport_name,
                        city = EXCLUDED.city,
                        state = EXCLUDED.state,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        is_hub = true
                    """,
                    (iata, name, city, state, lat, lon),
                )
    return len(HUB_AIRPORTS)


def load_weather(year: int | None = None) -> int:
    year = year or int(os.environ.get("SKYOPS_YEAR", "2024"))
    path = weather_json_path(year)
    if not path.exists():
        raise FileNotFoundError(f"Missing weather file {path}; run make download-weather")

    payloads = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for block in payloads:
        iata = block["airport_iata"]
        daily = block.get("daily") or {}
        dates = daily.get("time") or []
        for i, d in enumerate(dates):
            rows.append(
                (
                    iata,
                    d,
                    _idx(daily.get("temperature_2m_max"), i),
                    _idx(daily.get("temperature_2m_min"), i),
                    _idx(daily.get("precipitation_sum"), i),
                    _idx(daily.get("wind_speed_10m_max"), i),
                    _idx(daily.get("weather_code"), i),
                )
            )

    with warehouse_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM raw.weather_daily WHERE weather_date >= %s AND weather_date <= %s",
                (f"{year}-01-01", f"{year}-12-31"),
            )
            cur.executemany(
                """
                INSERT INTO raw.weather_daily (
                    airport_iata, weather_date, temp_max_c, temp_min_c, precip_mm, wind_max_kmh, weather_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (airport_iata, weather_date) DO UPDATE SET
                    temp_max_c = EXCLUDED.temp_max_c,
                    temp_min_c = EXCLUDED.temp_min_c,
                    precip_mm = EXCLUDED.precip_mm,
                    wind_max_kmh = EXCLUDED.wind_max_kmh,
                    weather_code = EXCLUDED.weather_code,
                    loaded_at = now()
                """,
                rows,
            )
            cur.execute(
                """
                INSERT INTO raw.ingestion_runs (source_name, finished_at, status, row_count, notes)
                VALUES ('weather_daily', now(), 'ok', %s, %s)
                """,
                (len(rows), str(year)),
            )
    return len(rows)


def _idx(seq, i):
    if not seq or i >= len(seq):
        return None
    return seq[i]


def run_fetch(year: int | None = None) -> int:
    """Ensure weather file exists, upsert airports, load weather."""
    from ingestion.fetch_weather import fetch_all

    year = year or int(os.environ.get("SKYOPS_YEAR", "2024"))
    upsert_airports()
    fetch_all(year)
    return load_weather(year)


if __name__ == "__main__":
    print(run_fetch())
