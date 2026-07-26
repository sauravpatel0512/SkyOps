"""Postgres connection helpers for SkyOps ingestion."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as PGConnection


def warehouse_dsn(
    *,
    host: str | None = None,
    port: str | None = None,
    user: str | None = None,
    password: str | None = None,
    dbname: str | None = None,
    sslmode: str | None = None,
) -> str:
    """Build a libpq-style DSN. Optional sslmode for managed Postgres (Neon/RDS)."""
    host = host if host is not None else os.environ.get("POSTGRES_HOST", "localhost")
    port = port if port is not None else os.environ.get("POSTGRES_PORT", "5432")
    user = user if user is not None else os.environ.get("POSTGRES_USER", "postgres")
    password = (
        password
        if password is not None
        else os.environ.get("POSTGRES_PASSWORD", "postgres")
    )
    dbname = dbname if dbname is not None else os.environ.get("POSTGRES_DB", "skyops")
    if sslmode is None:
        sslmode = os.environ.get("POSTGRES_SSLMODE", "").strip()

    parts = [
        f"host={host}",
        f"port={port}",
        f"user={user}",
        f"password={password}",
        f"dbname={dbname}",
    ]
    if sslmode:
        parts.append(f"sslmode={sslmode}")
    return " ".join(parts)


def cloud_warehouse_dsn() -> str:
    """DSN from CLOUD_POSTGRES_* (managed Postgres). Defaults sslmode=require."""
    host = os.environ.get("CLOUD_POSTGRES_HOST")
    if not host:
        raise ValueError(
            "CLOUD_POSTGRES_HOST is required for cloud_warehouse_dsn(); "
            "see .env.example and docs/RUNBOOK.md"
        )
    return warehouse_dsn(
        host=host,
        port=os.environ.get("CLOUD_POSTGRES_PORT", "5432"),
        user=os.environ.get("CLOUD_POSTGRES_USER", "postgres"),
        password=os.environ.get("CLOUD_POSTGRES_PASSWORD", ""),
        dbname=os.environ.get("CLOUD_POSTGRES_DB", "skyops"),
        sslmode=os.environ.get("CLOUD_POSTGRES_SSLMODE", "require"),
    )


@contextmanager
def warehouse_conn(
    *,
    use_cloud: bool = False,
) -> Generator[PGConnection, None, None]:
    dsn = cloud_warehouse_dsn() if use_cloud else warehouse_dsn()
    conn = psycopg2.connect(dsn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
