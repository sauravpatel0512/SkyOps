select
    origin_airport as airport_iata,
    date_trunc('month', fl_date)::date as month_start,
    count(*) as flight_count,
    sum(case when cancelled = 1 then 1 else 0 end) as cancelled_flights,
    avg(case when cancelled = 1 then 1.0 else 0.0 end) as cancel_rate,
    avg(dep_delay) filter (where cancelled = 0) as avg_dep_delay_min,
    avg(arr_delay) filter (where cancelled = 0) as avg_arr_delay_min,
    avg(is_on_time) filter (where cancelled = 0) as on_time_rate
from {{ ref('fct_flights') }}
group by 1, 2
