from flask import Flask, render_template
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import random
from urllib.parse import urlparse

app = Flask(__name__)

# Init NewsAPI client
newsapi = NewsApiClient(api_key="29f6df0c8a13495787c2980857314267")

# Cache raw API data
cached_raw_articles = None
cache_time = None
CACHE_DURATION = timedelta(minutes=10)

# --- Utility: safe URL filter ---
def safe_url(url):
    """Validate external URL. Return '#' if invalid or empty."""
    if not url:
        return "#"
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return "#"
    return url

app.jinja_env.filters['safe_url'] = safe_url  # Register as Jinja filter

@app.route("/")
def home():
    global cached_raw_articles, cache_time
    now = datetime.now()

    # Fetch new API data if cache expired
    if not cached_raw_articles or not cache_time or now - cache_time > CACHE_DURATION:
        categories = ["business", "entertainment", "health", "science", "sports", "technology"]
        category_articles = {}
        for cat in categories:
            try:
                res = newsapi.get_top_headlines(language="en", country="us", category=cat)
                articles = res.get("articles", [])
                for a in articles:
                    a["category"] = cat
                random.shuffle(articles)  # shuffle once per cache refresh
                category_articles[cat] = articles[:10]  # store more for randomness
            except Exception as e:
                print(f"Error fetching {cat}: {e}")
                category_articles[cat] = []
        cached_raw_articles = category_articles
        cache_time = now
    else:
        category_articles = cached_raw_articles

    # Flatten all articles for random selection
    all_articles_flat = [a for arts in category_articles.values() for a in arts if a]

    # Randomly pick main article
    main_article = random.choice(all_articles_flat) if all_articles_flat else {}

    # Remaining articles for grid and side
    remaining_articles = [a for a in all_articles_flat if a != main_article]
    random.shuffle(remaining_articles)
    grid_articles = remaining_articles[:6]
    side_articles = remaining_articles[6:12] if len(remaining_articles) > 6 else remaining_articles[6:]

    all_articles = {
        "main_article": main_article,
        "grid_articles": grid_articles,
        "side_articles": side_articles
    }

    # Random category cards (one per category)
    category_cards = {cat: random.choice(arts) if arts else {} for cat, arts in category_articles.items()}

    today = now.strftime("%A, %B %d, %Y")
    return render_template(
        "index.html",
        today=today,
        all_articles=all_articles,
        category_cards=category_cards
    )

if __name__ == "__main__":
    app.run(debug=True)
