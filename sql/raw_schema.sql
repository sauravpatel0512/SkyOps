-- Raw flight + weather tables for SkyOps.

CREATE TABLE IF NOT EXISTS raw.flights (
    fl_date            date NOT NULL,
    year               integer,
    month              integer,
    op_unique_carrier  text NOT NULL,
    op_carrier_fl_num  text,
    origin             text NOT NULL,
    dest               text NOT NULL,
    crs_dep_time       integer,
    dep_time           integer,
    dep_delay          double precision,
    taxi_out           double precision,
    taxi_in            double precision,
    crs_arr_time       integer,
    arr_time           integer,
    arr_delay          double precision,
    cancelled          double precision,
    diverted           double precision,
    crs_elapsed_time   double precision,
    actual_elapsed_time double precision,
    air_time           double precision,
    distance           double precision,
    carrier_delay      double precision,
    weather_delay      double precision,
    nas_delay          double precision,
    security_delay     double precision,
    late_aircraft_delay double precision,
    source_file        text,
    loaded_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_raw_flights_fl_date ON raw.flights (fl_date);
CREATE INDEX IF NOT EXISTS idx_raw_flights_origin ON raw.flights (origin);
CREATE INDEX IF NOT EXISTS idx_raw_flights_carrier ON raw.flights (op_unique_carrier);
CREATE INDEX IF NOT EXISTS idx_raw_flights_year_month ON raw.flights (year, month);

CREATE TABLE IF NOT EXISTS raw.weather_daily (
    airport_iata       text NOT NULL,
    weather_date       date NOT NULL,
    temp_max_c         double precision,
    temp_min_c         double precision,
    precip_mm          double precision,
    wind_max_kmh       double precision,
    weather_code       integer,
    loaded_at          timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (airport_iata, weather_date)
);

CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    run_id             bigserial PRIMARY KEY,
    source_name        text NOT NULL,
    started_at         timestamptz NOT NULL DEFAULT now(),
    finished_at        timestamptz,
    status             text NOT NULL,
    row_count          bigint,
    notes              text
);

CREATE TABLE IF NOT EXISTS raw.airports (
    iata_code          text PRIMARY KEY,
    airport_name       text,
    city               text,
    state              text,
    latitude           double precision NOT NULL,
    longitude          double precision NOT NULL,
    is_hub             boolean NOT NULL DEFAULT true
);
