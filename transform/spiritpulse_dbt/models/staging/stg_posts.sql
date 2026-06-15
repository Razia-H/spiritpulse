-- stg_posts.sql
-- Staging model: clean and type-cast raw social posts from DLT landing table.
-- Source: spiritpulse.social_posts (written by DLT)

{{ config(materialized='view', schema='spiritpulse') }}

with source as (
    select * from {{ source('spiritpulse_raw', 'social_posts') }}
),

cleaned as (
    select
        post_id,
        platform,
        brand_id,
        brand_name,
        brand_category,
        content,
        sentiment_label,
        sentiment_score::numeric(5,3)       as sentiment_score,
        likes::integer                       as likes,
        shares::integer                      as shares,
        comments::integer                    as comments,
        author_handle,
        author_followers::integer            as author_followers,
        hashtags,
        posted_at::timestamptz               as posted_at,
        ingested_at::timestamptz             as ingested_at,

        -- derived
        (likes + shares * 2 + comments * 3)  as engagement_score,
        date_trunc('hour', posted_at::timestamptz) as posted_hour,
        date_trunc('day',  posted_at::timestamptz) as posted_date

    from source
    where post_id is not null
      and brand_id is not null
      and sentiment_label in ('positive', 'negative', 'neutral')
)

select * from cleaned
