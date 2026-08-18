"""Unit tests for warehouse DSN helpers (no live Postgres required)."""

from __future__ import annotations

import pytest

from ingestion.db import cloud_warehouse_dsn, warehouse_dsn


def test_warehouse_dsn_defaults(monkeypatch):
    for key in (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_SSLMODE",
    ):
        monkeypatch.delenv(key, raising=False)
    dsn = warehouse_dsn()
    assert "host=localhost" in dsn
    assert "port=5432" in dsn
    assert "dbname=skyops" in dsn
    assert "sslmode=" not in dsn


def test_warehouse_dsn_includes_sslmode(monkeypatch):
    monkeypatch.setenv("POSTGRES_SSLMODE", "require")
    dsn = warehouse_dsn()
    assert "sslmode=require" in dsn


def test_cloud_warehouse_dsn_requires_host(monkeypatch):
    monkeypatch.delenv("CLOUD_POSTGRES_HOST", raising=False)
    with pytest.raises(ValueError, match="CLOUD_POSTGRES_HOST"):
        cloud_warehouse_dsn()


def test_cloud_warehouse_dsn_defaults_ssl_require(monkeypatch):
    monkeypatch.setenv("CLOUD_POSTGRES_HOST", "ep-example.neon.tech")
    monkeypatch.setenv("CLOUD_POSTGRES_USER", "skyops")
    monkeypatch.setenv("CLOUD_POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("CLOUD_POSTGRES_DB", "skyops")
    monkeypatch.delenv("CLOUD_POSTGRES_SSLMODE", raising=False)
    dsn = cloud_warehouse_dsn()
    assert "host=ep-example.neon.tech" in dsn
    assert "sslmode=require" in dsn
    assert "user=skyops" in dsn
