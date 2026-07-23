select
    origin_weather_bucket as weather_bucket,
    date_trunc('month', fl_date)::date as month_start,
    count(*) as flight_count,
    avg(arr_delay) filter (where cancelled = 0) as avg_arr_delay_min,
    avg(dep_delay) filter (where cancelled = 0) as avg_dep_delay_min,
    avg(is_on_time) filter (where cancelled = 0) as on_time_rate,
    avg(weather_delay) filter (where cancelled = 0) as avg_weather_delay_min,
    avg(origin_precip_mm) as avg_precip_mm,
    avg(origin_wind_max_kmh) as avg_wind_kmh
from {{ ref('fct_flights') }}
where origin_weather_bucket is not null
group by 1, 2
