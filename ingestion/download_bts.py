"""Download BTS On-Time monthly PREZIP archives for the demo year."""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

import requests

PREZIP_BASE = "https://transtats.bts.gov/PREZIP"
# Common filename patterns BTS has used
NAME_TEMPLATES = [
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip",
    "On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_{year}_{month}.zip",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Referer": "https://www.transtats.bts.gov/",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def bts_dir() -> Path:
    path = repo_root() / "data" / "raw" / "bts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def month_zip_path(year: int, month: int) -> Path:
    return bts_dir() / f"bts_ontime_{year}_{month:02d}.zip"


def csv_ready(year: int, month: int) -> bool:
    zpath = month_zip_path(year, month)
    if not zpath.exists() or zpath.stat().st_size < 1000:
        return False
    try:
        with zipfile.ZipFile(zpath) as zf:
            return any(n.lower().endswith(".csv") for n in zf.namelist())
    except zipfile.BadZipFile:
        return False


def try_download(url: str, dest: Path) -> bool:
    print(f"GET {url}")
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=120) as resp:
            if resp.status_code != 200:
                print(f"  -> HTTP {resp.status_code}")
                return False
            tmp = dest.with_suffix(".partial")
            with open(tmp, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
            tmp.replace(dest)
            if dest.stat().st_size < 1000:
                dest.unlink(missing_ok=True)
                print("  -> file too small, rejected")
                return False
            print(f"  -> saved {dest.name} ({dest.stat().st_size:,} bytes)")
            return True
    except requests.RequestException as exc:
        print(f"  -> error: {exc}")
        return False


def download_month(year: int, month: int) -> Path:
    dest = month_zip_path(year, month)
    if csv_ready(year, month):
        print(f"skip existing {dest.name}")
        return dest

    for tmpl in NAME_TEMPLATES:
        name = tmpl.format(year=year, month=month)
        if try_download(f"{PREZIP_BASE}/{name}", dest):
            if csv_ready(year, month):
                return dest
            dest.unlink(missing_ok=True)

    raise FileNotFoundError(
        f"Could not download BTS PREZIP for {year}-{month:02d}. "
        "Open https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ "
        f"and place a zip at {dest}"
    )


def download_year(year: int, months: list[int] | None = None) -> list[Path]:
    months = months or list(range(1, 13))
    paths = []
    errors = []
    for m in months:
        try:
            paths.append(download_month(year, m))
        except FileNotFoundError as exc:
            errors.append(str(exc))
    if errors and not paths:
        raise RuntimeError("\n".join(errors))
    if errors:
        print("Partial download; missing months:")
        for e in errors:
            print(" ", e)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download BTS on-time monthly zips")
    parser.add_argument("--year", type=int, default=int(os.environ.get("SKYOPS_YEAR", "2024")))
    parser.add_argument("--month", type=int, default=None, help="Single month 1-12")
    parser.add_argument("--months", type=str, default=None, help="Comma list e.g. 1,2,3")
    args = parser.parse_args(argv)

    months = None
    if args.month is not None:
        months = [args.month]
    elif args.months:
        months = [int(x) for x in args.months.split(",") if x.strip()]

    download_year(args.year, months)
    return 0


if __name__ == "__main__":
    sys.exit(main())
