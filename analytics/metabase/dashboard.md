# Metabase — SkyOps dashboards

## Connection

- Host: `postgres` (Compose network) or `localhost` from host
- Database: `skyops`
- Schema: `analytics`

## Panels

1. **Carrier reliability** — `mart_carrier_reliability` (on_time_rate, cancel_rate by carrier × month)
2. **Weather impact** — `mart_weather_impact` (avg_arr_delay_min by weather_bucket)
3. **Airport ops** — `mart_airport_ops` (top origin delay)
4. **Routes** — `mart_route_performance` (busiest OD pairs)
