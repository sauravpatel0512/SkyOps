select
    upper(trim(iata_code)) as iata_code,
    airport_name,
    city,
    state,
    latitude,
    longitude,
    is_hub
from {{ source('skyops_raw', 'airports') }}
