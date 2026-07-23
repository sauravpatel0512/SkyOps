"""Load small CI fixture into raw tables (no full BTS download)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ingestion.db import warehouse_conn
from ingestion.load_flights import _frame_to_copy_csv
from ingestion.load_weather import upsert_airports

FLIGHT_COLS = [
    "fl_date",
    "year",
    "month",
    "op_unique_carrier",
    "op_carrier_fl_num",
    "origin",
    "dest",
    "crs_dep_time",
    "dep_time",
    "dep_delay",
    "taxi_out",
    "taxi_in",
    "crs_arr_time",
    "arr_time",
    "arr_delay",
    "cancelled",
    "diverted",
    "crs_elapsed_time",
    "actual_elapsed_time",
    "air_time",
    "distance",
    "carrier_delay",
    "weather_delay",
    "nas_delay",
    "security_delay",
    "late_aircraft_delay",
    "source_file",
]


def fixture_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "flights_sample.csv"


def load_ci_fixture() -> None:
    upsert_airports()
    df = pd.read_csv(fixture_path(), parse_dates=["fl_date"])
    df["fl_date"] = df["fl_date"].dt.date
    df["source_file"] = "flights_sample.csv"
    int_cols = ["year", "month", "crs_dep_time", "dep_time", "crs_arr_time", "arr_time"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
    float_cols = [
        "dep_delay",
        "taxi_out",
        "taxi_in",
        "arr_delay",
        "cancelled",
        "diverted",
        "crs_elapsed_time",
        "actual_elapsed_time",
        "air_time",
        "distance",
        "carrier_delay",
        "weather_delay",
        "nas_delay",
        "security_delay",
        "late_aircraft_delay",
    ]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[FLIGHT_COLS]

    weather_rows = [
        ("ATL", "2024-01-01", 12.0, 2.0, 0.0, 15.0, 1),
        ("ATL", "2024-01-02", 8.0, -1.0, 12.5, 40.0, 61),
        ("ATL", "2024-01-03", 10.0, 0.0, 0.0, 18.0, 2),
        ("ATL", "2024-01-04", 11.0, 1.0, 0.0, 14.0, 1),
        ("ORD", "2024-01-01", -5.0, -12.0, 2.0, 35.0, 71),
        ("ORD", "2024-01-02", -2.0, -9.0, 0.0, 20.0, 3),
        ("ORD", "2024-01-04", 0.0, -6.0, 1.0, 22.0, 51),
        ("JFK", "2024-01-01", 5.0, -1.0, 5.0, 45.0, 63),
        ("JFK", "2024-01-02", 6.0, 0.0, 0.2, 18.0, 2),
        ("JFK", "2024-01-03", 4.0, -2.0, 0.0, 16.0, 1),
        ("LAX", "2024-01-01", 18.0, 10.0, 0.0, 12.0, 0),
        ("LAX", "2024-01-02", 19.0, 11.0, 0.0, 10.0, 0),
        ("LAX", "2024-01-03", 17.0, 9.0, 0.0, 11.0, 0),
        ("DFW", "2024-01-01", 10.0, 1.0, 1.0, 25.0, 51),
        ("DFW", "2024-01-02", 12.0, 2.0, 0.0, 20.0, 1),
        ("SEA", "2024-01-01", 7.0, 2.0, 8.0, 22.0, 61),
        ("SEA", "2024-01-02", 6.0, 1.0, 5.0, 28.0, 61),
        ("DEN", "2024-01-01", 0.0, -8.0, 3.0, 30.0, 71),
        ("DEN", "2024-01-03", 2.0, -5.0, 0.0, 18.0, 2),
        ("SFO", "2024-01-01", 14.0, 8.0, 0.0, 15.0, 1),
        ("SFO", "2024-01-02", 13.0, 7.0, 2.0, 20.0, 51),
        ("MCO", "2024-01-01", 24.0, 15.0, 0.0, 12.0, 0),
        ("MIA", "2024-01-02", 26.0, 18.0, 1.0, 18.0, 51),
        ("MIA", "2024-01-04", 27.0, 19.0, 0.0, 14.0, 1),
        ("BOS", "2024-01-03", 3.0, -4.0, 0.5, 24.0, 51),
        ("PHX", "2024-01-04", 20.0, 8.0, 0.0, 16.0, 0),
        ("EWR", "2024-01-04", 4.0, -2.0, 2.0, 30.0, 61),
        ("MDW", "2024-01-04", 1.0, -5.0, 0.0, 18.0, 2),
        ("AUS", "2024-01-03", 15.0, 5.0, 0.0, 12.0, 1),
        ("PDX", "2024-01-04", 8.0, 2.0, 4.0, 20.0, 61),
    ]

    with warehouse_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE raw.flights")
            cur.execute("TRUNCATE raw.weather_daily")
            buf = _frame_to_copy_csv(df, FLIGHT_COLS)
            cur.copy_expert(
                f"COPY raw.flights ({', '.join(FLIGHT_COLS)}) FROM STDIN WITH (FORMAT csv, NULL '')",
                buf,
            )
            cur.executemany(
                """
                INSERT INTO raw.weather_daily (
                    airport_iata, weather_date, temp_max_c, temp_min_c, precip_mm, wind_max_kmh, weather_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                weather_rows,
            )
    print(f"CI fixture loaded: {len(df)} flights, {len(weather_rows)} weather rows")


if __name__ == "__main__":
    load_ci_fixture()
