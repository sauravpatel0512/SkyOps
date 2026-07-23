select
    f.*,
    w.temp_max_c as origin_temp_max_c,
    w.temp_min_c as origin_temp_min_c,
    w.precip_mm as origin_precip_mm,
    w.wind_max_kmh as origin_wind_max_kmh,
    w.weather_code as origin_weather_code,
    coalesce(w.weather_bucket, 'unknown') as origin_weather_bucket
from {{ ref('stg_flights') }} f
left join {{ ref('stg_weather_daily') }} w
    on f.origin = w.airport_iata
   and f.fl_date = w.weather_date
