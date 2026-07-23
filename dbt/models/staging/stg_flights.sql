select
    fl_date,
    year,
    month,
    upper(trim(op_unique_carrier)) as op_unique_carrier,
    op_carrier_fl_num,
    upper(trim(origin)) as origin,
    upper(trim(dest)) as dest,
    crs_dep_time,
    dep_time,
    dep_delay,
    taxi_out,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    coalesce(cancelled, 0) as cancelled,
    coalesce(diverted, 0) as diverted,
    crs_elapsed_time,
    actual_elapsed_time,
    air_time,
    distance,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    case
        when coalesce(cancelled, 0) = 1 then null
        when arr_delay is null then null
        when arr_delay <= 15 then 1
        else 0
    end as is_on_time
from {{ source('skyops_raw', 'flights') }}
where fl_date is not null
  and origin is not null
  and dest is not null
  and op_unique_carrier is not null
