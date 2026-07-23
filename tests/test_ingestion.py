"""Unit tests for SkyOps ingestion helpers."""

from __future__ import annotations

from ingestion.hubs import HUB_AIRPORTS, COLUMN_ALIASES
from ingestion.download_bts import month_zip_path


def test_hub_count():
    assert len(HUB_AIRPORTS) >= 25
    codes = [h[0] for h in HUB_AIRPORTS]
    assert "ATL" in codes and "JFK" in codes


def test_column_aliases_cover_targets():
    assert "FlightDate" in COLUMN_ALIASES
    assert "Origin" in COLUMN_ALIASES


def test_month_zip_naming():
    p = month_zip_path(2024, 3)
    assert p.name == "bts_ontime_2024_03.zip"
