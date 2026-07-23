with carriers as (
    select distinct op_unique_carrier as carrier_code
    from {{ ref('stg_flights') }}
)
select
    c.carrier_code,
    coalesce(n.carrier_name, c.carrier_code) as carrier_name
from carriers c
left join {{ ref('carrier_names') }} n
    on c.carrier_code = n.carrier_code
