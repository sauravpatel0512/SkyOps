select
    origin_airport,
    dest_airport,
    date_trunc('month', fl_date)::date as month_start,
    count(*) as flight_count,
    avg(arr_delay) filter (where cancelled = 0) as avg_arr_delay_min,
    avg(is_on_time) filter (where cancelled = 0) as on_time_rate,
    avg(distance) as avg_distance_miles
from {{ ref('fct_flights') }}
group by 1, 2, 3
having count(*) >= 1
