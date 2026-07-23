# Failure notes — bugs that actually happened

## 1. BTS PREZIP returns HTTP 403

**Symptom:** `requests.get(https://transtats.bts.gov/PREZIP/...)` fails with 403; empty or tiny files.

**Cause:** TranStats blocks non-browser clients / missing Referer.

**Fix:** Send browser-like `User-Agent` + `Referer: https://www.transtats.bts.gov/`. If still blocked, download via browser and drop zips into `data/raw/bts/bts_ontime_{year}_{mm}.zip`.

## 2. pandas float times break COPY

**Symptom:** `invalid input syntax for type integer: "851.0"` during `COPY raw.flights`.

**Cause:** BTS time columns load as floats in pandas.

**Fix:** Round and cast to pandas `Int64` before COPY; serialize empties as NULL.

## 3. dbt CI crash on protobuf 7

**Symptom:** `TypeError: MessageToJson() got an unexpected keyword argument 'including_default_value_fields'`.

**Cause:** `dbt-core` 1.7.x incompatible with protobuf 5+/7+.

**Fix:** Pin `protobuf>=4.25.3,<5` and `dbt-core==1.7.14` in requirements.

## 3. Validate-before-download fails empty cache

**Symptom:** First DAG run fails `validate_sources` with no zips.

**Fix:** DAG order is download → validate → load → weather → dbt.

## 4. Host port 5432 already taken

**Symptom:** `password authentication failed for user postgres` from the host against `localhost:5432`.

**Cause:** Another local Postgres was bound to 5432; Compose published SkyOps on the same port.

**Fix:** Map warehouse to host **5433** (`POSTGRES_PORT=5433` in `.env` / compose). Inside Compose, services still use hostname `postgres:5432`.

