with seen as (
    select origin as iata_code from {{ ref('stg_flights') }}
    union
    select dest as iata_code from {{ ref('stg_flights') }}
)
select
    s.iata_code,
    coalesce(a.airport_name, s.iata_code) as airport_name,
    a.city,
    a.state,
    a.latitude,
    a.longitude,
    coalesce(a.is_hub, false) as is_hub
from seen s
left join {{ ref('stg_airports') }} a
    on s.iata_code = a.iata_code
