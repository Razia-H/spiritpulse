-- mart_trending_hashtags.sql
-- Mart: hashtag trend analysis — which tags are gaining momentum.
-- Powers the FastAPI /trends endpoint.

{{ config(materialized='table', schema='spiritpulse') }}

with posts as (
    select * from {{ ref('stg_posts') }}
),

-- Explode comma-separated hashtags into individual rows
exploded as (
    select
        post_id,
        brand_id,
        brand_name,
        brand_category,
        sentiment_label,
        sentiment_score,
        engagement_score,
        posted_date,
        trim(tag) as hashtag
    from posts,
    lateral unnest(string_to_array(hashtags, ',')) as tag
    where hashtags is not null
      and hashtags != ''
),

aggregated as (
    select
        hashtag,
        brand_id,
        brand_name,
        brand_category,
        posted_date                                             as report_date,
        count(*)                                                as mention_count,
        round(avg(sentiment_score)::numeric, 3)                as avg_sentiment,
        sum(engagement_score)                                   as total_engagement,
        count(*) filter (where sentiment_label = 'positive')   as positive_mentions,
        count(*) filter (where sentiment_label = 'negative')   as negative_mentions
    from exploded
    where hashtag != ''
    group by
        hashtag,
        brand_id,
        brand_name,
        brand_category,
        posted_date
),

with_rank as (
    select
        *,
        rank() over (
            partition by report_date
            order by mention_count desc, total_engagement desc
        ) as trend_rank
    from aggregated
)

select * from with_rank
where trend_rank <= 20
order by report_date desc, trend_rank asc
