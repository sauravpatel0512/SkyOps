-- Airflow metadata database (separate from warehouse DB skyops).
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
