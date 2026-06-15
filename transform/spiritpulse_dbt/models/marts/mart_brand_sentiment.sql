-- mart_brand_sentiment.sql
-- Mart: aggregated sentiment metrics per brand per day.
-- This is the primary table the FastAPI /sentiment endpoint reads from.

{{ config(materialized='table', schema='spiritpulse') }}

with posts as (
    select * from {{ ref('stg_posts') }}
),

daily_sentiment as (
    select
        brand_id,
        brand_name,
        brand_category,
        posted_date                                         as report_date,
        count(*)                                            as total_posts,
        count(*) filter (where sentiment_label = 'positive') as positive_count,
        count(*) filter (where sentiment_label = 'negative') as negative_count,
        count(*) filter (where sentiment_label = 'neutral')  as neutral_count,
        round(avg(sentiment_score)::numeric, 3)             as avg_sentiment_score,
        round(
            count(*) filter (where sentiment_label = 'positive')::numeric
            / nullif(count(*), 0) * 100, 1
        )                                                   as positive_pct,
        round(
            count(*) filter (where sentiment_label = 'negative')::numeric
            / nullif(count(*), 0) * 100, 1
        )                                                   as negative_pct,
        sum(engagement_score)                               as total_engagement,
        round(avg(engagement_score)::numeric, 1)            as avg_engagement,
        sum(likes)                                          as total_likes,
        sum(shares)                                         as total_shares,
        sum(comments)                                       as total_comments,
        max(ingested_at)                                    as last_ingested_at

    from posts
    group by
        brand_id,
        brand_name,
        brand_category,
        posted_date
),

with_rank as (
    select
        *,
        case
            when avg_sentiment_score >= 0.65 then 'bullish'
            when avg_sentiment_score >= 0.45 then 'neutral'
            else 'bearish'
        end as sentiment_signal,
        rank() over (
            partition by report_date
            order by avg_sentiment_score desc
        ) as daily_sentiment_rank
    from daily_sentiment
)

select * from with_rank
order by report_date desc, daily_sentiment_rank asc
