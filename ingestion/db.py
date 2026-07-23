"""Postgres connection helpers for SkyOps ingestion."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as PGConnection


def warehouse_dsn() -> str:
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    db = os.environ.get("POSTGRES_DB", "skyops")
    return f"host={host} port={port} user={user} password={password} dbname={db}"


@contextmanager
def warehouse_conn() -> Generator[PGConnection, None, None]:
    conn = psycopg2.connect(warehouse_dsn())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
