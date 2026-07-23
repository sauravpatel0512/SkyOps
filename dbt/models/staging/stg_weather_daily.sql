select
    upper(trim(airport_iata)) as airport_iata,
    weather_date,
    temp_max_c,
    temp_min_c,
    coalesce(precip_mm, 0) as precip_mm,
    coalesce(wind_max_kmh, 0) as wind_max_kmh,
    weather_code,
    case
        when coalesce(precip_mm, 0) >= 10 or coalesce(wind_max_kmh, 0) >= 40 then 'severe'
        when coalesce(precip_mm, 0) >= 1 or coalesce(wind_max_kmh, 0) >= 25 then 'adverse'
        else 'fair'
    end as weather_bucket
from {{ source('skyops_raw', 'weather_daily') }}
