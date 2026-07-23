# Validation log

| Date | What ran | Result | Notes |
|------|----------|--------|-------|
| 2026-07-22 | `make download` (BTS 2024 × 12 + Open-Meteo hubs) | OK | ~354 MB BTS zips; weather JSON for 30 hubs |
| 2026-07-22 | Load `raw.flights` + `raw.weather_daily` + dbt build | OK | **7,079,061** flights; dbt PASS=42 WARN=0 ERROR=0 |
| 2026-07-22 | Mart evidence charts | OK | `docs/screenshots/metabase_carrier_reliability.png`, `metabase_weather_impact.png` |

Sample signal: severe origin weather ≈ **21.7 min** avg arrival delay vs **3.9 min** fair (2024 marts).
