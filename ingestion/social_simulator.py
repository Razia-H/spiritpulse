"""
social_simulator.py
Generates realistic fake social media posts about alcohol brands.
Simulates what a real Twitter/Reddit API would return.
"""

import random
import uuid
from datetime import datetime, timezone, timedelta
from faker import Faker

fake = Faker()

BRANDS = [
    {"id": "jack_daniels", "name": "Jack Daniel's", "category": "whiskey", "hashtags": ["#JackDaniels", "#JD", "#Whiskey", "#Tennessee"]},
    {"id": "modelo", "name": "Modelo", "category": "beer", "hashtags": ["#Modelo", "#ModeloEspecial", "#Beer", "#CervezaModelo"]},
    {"id": "guinness", "name": "Guinness", "category": "stout", "hashtags": ["#Guinness", "#GuinnessStout", "#IrishBeer", "#Stout"]},
    {"id": "hendricks", "name": "Hendrick's Gin", "category": "gin", "hashtags": ["#HendricksGin", "#Gin", "#GinAndTonic", "#CraftGin"]},
    {"id": "don_julio", "name": "Don Julio", "category": "tequila", "hashtags": ["#DonJulio", "#Tequila", "#DonJulio1942", "#Agave"]},
    {"id": "whispering_angel", "name": "Whispering Angel", "category": "rose_wine", "hashtags": ["#WhisperingAngel", "#RoseWine", "#Rose", "#ProvenceRose"]},
]

SENTIMENT_TEMPLATES = {
    "positive": [
        "Just had my first {brand} and I'm absolutely hooked. This is incredible! {hashtag}",
        "Nothing beats a cold {brand} on a Friday evening. Pure perfection. {hashtag}",
        "{brand} never disappoints. Best in the game by far. {hashtag} {hashtag2}",
        "Tried {brand} at a rooftop bar last night — totally worth the hype. {hashtag}",
        "Birthday dinner sorted — {brand} flowing all night. 🥂 {hashtag}",
        "If you haven't tried {brand} yet, you are seriously missing out. {hashtag}",
        "The smoothness of {brand} is unmatched. Five stars every time. {hashtag}",
    ],
    "negative": [
        "Honestly disappointed with {brand} lately. Quality has really dropped. {hashtag}",
        "Ordered {brand} at the bar and it tasted completely off. What happened? {hashtag}",
        "Way overpriced for what you get with {brand}. Not worth it anymore. {hashtag}",
        "Had a terrible experience with {brand} last night. Won't be ordering again. {hashtag}",
        "The new {brand} formula just doesn't hit the same. Bring back the original. {hashtag}",
    ],
    "neutral": [
        "Anyone else drinking {brand} tonight? {hashtag}",
        "Seeing {brand} everywhere lately. Curious to try it. {hashtag}",
        "What's the best way to drink {brand}? Asking for a friend. {hashtag}",
        "Just picked up a bottle of {brand} for the weekend. {hashtag}",
        "{brand} or {brand2}? Hard choice tonight. {hashtag}",
        "The {brand} display at the store was pretty impressive tbh. {hashtag}",
    ],
}

PLATFORMS = ["twitter", "reddit", "instagram", "tiktok"]

SENTIMENT_WEIGHTS = {
    "positive": 0.55,
    "negative": 0.20,
    "neutral": 0.25,
}

SENTIMENT_SCORES = {
    "positive": lambda: round(random.uniform(0.55, 0.99), 3),
    "negative": lambda: round(random.uniform(0.01, 0.40), 3),
    "neutral":  lambda: round(random.uniform(0.38, 0.62), 3),
}


def _pick_sentiment() -> str:
    return random.choices(
        list(SENTIMENT_WEIGHTS.keys()),
        weights=list(SENTIMENT_WEIGHTS.values()),
        k=1
    )[0]


def _build_post_text(brand: dict, sentiment: str) -> str:
    templates = SENTIMENT_TEMPLATES[sentiment]
    template = random.choice(templates)
    hashtag = random.choice(brand["hashtags"])
    hashtag2 = random.choice(brand["hashtags"])
    other_brand = random.choice([b for b in BRANDS if b["id"] != brand["id"]])
    return template.format(
        brand=brand["name"],
        hashtag=hashtag,
        hashtag2=hashtag2,
        brand2=other_brand["name"],
    )


def generate_posts(count: int = 50, hours_back: int = 24) -> list[dict]:
    """
    Generate a list of fake social media posts about alcohol brands.
    Returns records ready to be loaded by DLT.
    """
    posts = []
    now = datetime.now(timezone.utc)

    for _ in range(count):
        brand = random.choice(BRANDS)
        sentiment = _pick_sentiment()
        posted_at = now - timedelta(
            hours=random.uniform(0, hours_back),
            minutes=random.uniform(0, 59),
        )

        post = {
            "post_id": str(uuid.uuid4()),
            "platform": random.choice(PLATFORMS),
            "brand_id": brand["id"],
            "brand_name": brand["name"],
            "brand_category": brand["category"],
            "content": _build_post_text(brand, sentiment),
            "sentiment_label": sentiment,
            "sentiment_score": SENTIMENT_SCORES[sentiment](),
            "likes": random.randint(0, 5000),
            "shares": random.randint(0, 1000),
            "comments": random.randint(0, 500),
            "author_handle": fake.user_name(),
            "author_followers": random.randint(10, 500000),
            "hashtags": ",".join(random.sample(brand["hashtags"], k=min(2, len(brand["hashtags"])))),
            "posted_at": posted_at.isoformat(),
            "ingested_at": now.isoformat(),
        }
        posts.append(post)

    return posts


def generate_brands() -> list[dict]:
    """Return the master brand list as seed records."""
    return [
        {
            "brand_id": b["id"],
            "brand_name": b["name"],
            "category": b["category"],
            "primary_hashtag": b["hashtags"][0],
        }
        for b in BRANDS
    ]


if __name__ == "__main__":
    posts = generate_posts(10)
    for p in posts:
        print(f"[{p['sentiment_label'].upper():8}] {p['brand_name']:20} → {p['content'][:60]}...")
