select
    run_id,
    lower(trim(source_name)) as source_name,
    started_at,
    finished_at,
    lower(trim(status)) as status,
    row_count,
    notes
from {{ source('skyops_raw', 'ingestion_runs') }}
where source_name is not null
  and status is not null
