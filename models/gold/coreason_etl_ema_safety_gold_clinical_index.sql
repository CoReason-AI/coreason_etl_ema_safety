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
    schema='gold'
) }}

WITH base_medicines AS (
    SELECT
        m.coreason_id,
        m.ema_product_number,
        m.brand_name,
        m.active_substances_array,
        NULLIF(TRIM(r.raw_data->>'Therapeutic indication'), '') AS therapeutic_indication
    FROM {{ ref('coreason_etl_ema_safety_silver_medicines_base') }} m
    LEFT JOIN {{ source('ema_safety', 'coreason_etl_ema_safety_bronze_medicines') }} r
        ON m.coreason_id = r.coreason_id
)

SELECT
    coreason_id,
    ema_product_number,
    brand_name,
    active_substances_array,
    therapeutic_indication,
    -- Concatenate into a clean text-searchable view combining the brand_name, active_substances_array, and indication data for RAG vector databases
    CONCAT_WS(' | ',
        'Brand Name: ' || COALESCE(brand_name, 'Unknown'),
        'Active Substances: ' || (
            SELECT string_agg(sub, ', ')
            FROM jsonb_array_elements_text(CASE WHEN jsonb_typeof(active_substances_array) = 'array' THEN active_substances_array ELSE '[]'::jsonb END) AS sub
        ),
        'Indication: ' || COALESCE(therapeutic_indication, 'Unknown')
    ) AS clinical_index_text
FROM base_medicines
