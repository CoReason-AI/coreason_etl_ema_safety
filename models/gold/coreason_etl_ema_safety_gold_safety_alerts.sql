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

WITH medicines AS (
    SELECT
        coreason_id,
        ema_product_number,
        brand_name,
        authorisation_status,
        active_substances_array,
        atc_codes_array
    FROM {{ ref('coreason_etl_ema_safety_silver_medicines_base') }}
),

referrals AS (
    SELECT
        coreason_id,
        NULLIF(TRIM(raw_data->>'Referral name'), '') AS referral_name,
        NULLIF(TRIM(raw_data->>'International non-proprietary name (INN) / common name'), '') AS referral_inn,
        NULLIF(TRIM(raw_data->>'Current status'), '') AS current_status,
        NULLIF(TRIM(raw_data->>'Referral type'), '') AS referral_type
    FROM {{ source('ema_safety', 'coreason_etl_ema_safety_bronze_referrals') }}
),

psusa AS (
    SELECT
        coreason_id,
        NULLIF(TRIM(raw_data->>'Medicine name'), '') AS psusa_medicine_name,
        NULLIF(TRIM(raw_data->>'Active substance'), '') AS psusa_active_substance,
        NULLIF(TRIM(raw_data->>'Outcome'), '') AS psusa_outcome
    FROM {{ source('ema_safety', 'coreason_etl_ema_safety_bronze_periodic_safety_update_report') }}
)

SELECT
    m.coreason_id,
    m.ema_product_number,
    m.brand_name,
    m.authorisation_status,
    m.active_substances_array,
    m.atc_codes_array,
    r.referral_name,
    r.current_status AS referral_status,
    r.referral_type,
    p.psusa_outcome
FROM medicines m
LEFT JOIN referrals r
    ON m.brand_name = r.referral_name
    OR EXISTS (
        SELECT 1
        FROM jsonb_array_elements_text(m.active_substances_array) AS sub
        WHERE r.referral_inn ILIKE '%' || sub || '%'
    )
LEFT JOIN psusa p
    ON m.brand_name = p.psusa_medicine_name
    OR EXISTS (
        SELECT 1
        FROM jsonb_array_elements_text(m.active_substances_array) AS sub
        WHERE p.psusa_active_substance ILIKE '%' || sub || '%'
    )
