-- Analytics objects are created by dbt; keep grant-ready schema.
CREATE SCHEMA IF NOT EXISTS analytics;
GRANT ALL ON SCHEMA analytics TO postgres;
GRANT ALL ON SCHEMA staging TO postgres;
