-- Copyright (c) 2026 CoReason, Inc.
--
-- This software is proprietary and dual-licensed.
-- Licensed under the Prosperity Public License 3.0 (the "License").
-- A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
-- For details, see the LICENSE file.
-- Commercial use beyond a 30-day trial requires a separate license.
--
-- Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

{{ config(
    materialized='table',
    schema='silver'
) }}

WITH source_data AS (
    SELECT
        coreason_id,
        source_file_url,
        ingestion_ts,
        raw_data
    FROM {{ source('ema_safety', 'ema_medicines_raw') }}
)

SELECT
    coreason_id,
    source_file_url,
    ingestion_ts,
    NULLIF(TRIM(raw_data->>'Product number'), '') AS ema_product_number,
    NULLIF(TRIM(raw_data->>'Medicine name'), '') AS brand_name,
    NULLIF(TRIM(raw_data->>'Authorisation status'), '') AS authorisation_status,

    -- Array Generation: Active substance
    CASE
        WHEN NULLIF(TRIM(raw_data->>'Active substance'), '') IS NOT NULL
        THEN to_jsonb(string_to_array(raw_data->>'Active substance', ', '))
        ELSE '[]'::jsonb
    END AS active_substances_array,

    -- Array Generation: ATC code
    CASE
        WHEN NULLIF(TRIM(raw_data->>'ATC code'), '') IS NOT NULL
        THEN to_jsonb(string_to_array(raw_data->>'ATC code', ', '))
        ELSE '[]'::jsonb
    END AS atc_codes_array

FROM source_data
