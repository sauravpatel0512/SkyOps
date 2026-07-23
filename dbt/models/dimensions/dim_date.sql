with bounds as (
    select
        min(fl_date) as min_d,
        max(fl_date) as max_d
    from {{ ref('stg_flights') }}
),
spine as (
    select generate_series(min_d, max_d, interval '1 day')::date as date_day
    from bounds
    where min_d is not null
)
select
    date_day,
    extract(year from date_day)::int as year,
    extract(month from date_day)::int as month,
    extract(dow from date_day)::int as day_of_week,
    to_char(date_day, 'YYYY-MM') as year_month
from spine
