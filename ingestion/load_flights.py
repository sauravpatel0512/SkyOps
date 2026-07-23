"""Load BTS monthly zips into raw.flights (idempotent per year-month)."""

from __future__ import annotations

import io
import zipfile

import pandas as pd

from ingestion.db import warehouse_conn
from ingestion.download_bts import csv_ready, month_zip_path
from ingestion.hubs import COLUMN_ALIASES

TARGET_COLS = {
    "FlightDate": "fl_date",
    "Year": "year",
    "Month": "month",
    "Reporting_Airline": "op_unique_carrier",
    "Flight_Number_Reporting_Airline": "op_carrier_fl_num",
    "Origin": "origin",
    "Dest": "dest",
    "CRSDepTime": "crs_dep_time",
    "DepTime": "dep_time",
    "DepDelay": "dep_delay",
    "TaxiOut": "taxi_out",
    "TaxiIn": "taxi_in",
    "CRSArrTime": "crs_arr_time",
    "ArrTime": "arr_time",
    "ArrDelay": "arr_delay",
    "Cancelled": "cancelled",
    "Diverted": "diverted",
    "CRSElapsedTime": "crs_elapsed_time",
    "ActualElapsedTime": "actual_elapsed_time",
    "AirTime": "air_time",
    "Distance": "distance",
    "CarrierDelay": "carrier_delay",
    "WeatherDelay": "weather_delay",
    "NASDelay": "nas_delay",
    "SecurityDelay": "security_delay",
    "LateAircraftDelay": "late_aircraft_delay",
}


def _resolve_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    lower_map = {c.lower(): c for c in df.columns}
    for canonical, aliases in COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            if alias in df.columns:
                found = alias
                break
            if alias.lower() in lower_map:
                found = lower_map[alias.lower()]
                break
        if found is None:
            raise KeyError(f"Missing BTS column for {canonical}; have {list(df.columns)[:20]}")
        rename[found] = TARGET_COLS[canonical]
    return df.rename(columns=rename)[list(TARGET_COLS.values())]


def read_month_frame(year: int, month: int) -> pd.DataFrame:
    zpath = month_zip_path(year, month)
    if not csv_ready(year, month):
        raise FileNotFoundError(f"Missing BTS zip for {year}-{month:02d}: {zpath}")
    with zipfile.ZipFile(zpath) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise FileNotFoundError(f"No CSV in {zpath}")
        with zf.open(csv_names[0]) as fh:
            chunks = []
            for chunk in pd.read_csv(fh, low_memory=False, chunksize=200_000):
                chunks.append(_resolve_columns(chunk))
    df = pd.concat(chunks, ignore_index=True)
    df["fl_date"] = pd.to_datetime(df["fl_date"]).dt.date
    df["source_file"] = zpath.name
    df["origin"] = df["origin"].astype(str).str.strip().str.upper()
    df["dest"] = df["dest"].astype(str).str.strip().str.upper()
    df["op_unique_carrier"] = df["op_unique_carrier"].astype(str).str.strip().str.upper()
    df["op_carrier_fl_num"] = df["op_carrier_fl_num"].astype(str)

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
    return df


def _frame_to_copy_csv(df: pd.DataFrame, out_cols: list[str]) -> io.StringIO:
    """Serialize for COPY: empty string = NULL, ints without .0."""
    buf = io.StringIO()
    export = df[out_cols].copy()
    for col in export.columns:
        if str(export[col].dtype) == "Int64":
            export[col] = export[col].astype(object).where(export[col].notna(), None)
            export[col] = export[col].apply(lambda x: "" if x is None else str(int(x)))
        else:
            export[col] = export[col].astype(object).where(pd.notnull(export[col]), None)
            export[col] = export[col].apply(lambda x: "" if x is None else str(x))
    export.to_csv(buf, index=False, header=False)
    buf.seek(0)
    return buf


def load_month(year: int, month: int) -> int:
    df = read_month_frame(year, month)
    with warehouse_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM raw.flights WHERE year = %s AND month = %s",
                (year, month),
            )
            out_cols = [
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
            buf = _frame_to_copy_csv(df, out_cols)
            cur.copy_expert(
                f"COPY raw.flights ({', '.join(out_cols)}) FROM STDIN WITH (FORMAT csv, NULL '')",
                buf,
            )
            cur.execute(
                """
                INSERT INTO raw.ingestion_runs (source_name, finished_at, status, row_count, notes)
                VALUES (%s, now(), 'ok', %s, %s)
                """,
                ("bts_flights", len(df), f"{year}-{month:02d}"),
            )
    return len(df)


def load_available_months(year: int) -> int:
    total = 0
    for month in range(1, 13):
        if csv_ready(year, month):
            n = load_month(year, month)
            print(f"loaded {year}-{month:02d}: {n:,} rows")
            total += n
        else:
            print(f"skip missing {year}-{month:02d}")
    return total


def run_load(year: int | None = None) -> int:
    import os

    year = year or int(os.environ.get("SKYOPS_YEAR", "2024"))
    return load_available_months(year)


if __name__ == "__main__":
    print(run_load())
