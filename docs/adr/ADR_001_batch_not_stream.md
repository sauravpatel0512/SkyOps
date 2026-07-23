# ADR 001 — Batch ELT for SkyOps (not streaming)

## Status

Accepted

## Context

SkyOps analyzes historical US airline on-time performance enriched with daily weather. Questions are monthly reliability and weather correlation, not sub-minute alerting.

## Decision

Use Airflow + dbt + Postgres + Metabase. Do not add Kafka/Spark/Flink here.

## Consequences

- Clear batch warehouse story for US internships
- Streaming covered separately by NexusFlow-X
- Multi-year scale can move to RainLift (Iceberg) later
