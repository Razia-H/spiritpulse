-- stg_brands.sql
-- Staging model: clean brand master list from DLT landing table.
-- Source: spiritpulse.brands (written by DLT)

{{ config(materialized='view', schema='spiritpulse') }}

with source as (
    select * from {{ source('spiritpulse_raw', 'brands') }}
),

cleaned as (
    select
        brand_id,
        brand_name,
        category,
        primary_hashtag,
        _dlt_load_id,
        _dlt_id
    from source
    where brand_id is not null
)

select * from cleaned
