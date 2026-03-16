"""
engine/agents/scraping_agent.py
================================
Sprint 4 Final: 14 sources.

المصادر:
    1.  Reddit          (7 subreddits)
    2.  HackerNews      (async concurrent)
    3.  Dev.to          (top articles)
    4.  Medium          (5 tags)
    5.  GitHub Trending (daily + weekly)
    6.  StackOverflow   (hot questions)
    7.  YouTube         (4 channels)
    8.  ProductHunt     (RSS)
    9.  Google News     (4 queries)
    10. Google Trends   (3 regions)
    11. Twitter/Nitter  (8 hashtags)
    12. LinkedIn        (RSS aggregators)
    13. TikTok          (Creative Center + RSS)   ← جديد
    14. Instagram       (hashtags + insights RSS) ← جديد
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.utils.logger import get_logger

from engine.scraping_sources.reddit_scraper          import scrape_reddit
from engine.scraping_sources.hackernews_scraper       import scrape_hackernews
from engine.scraping_sources.devto_scraper            import scrape_devto
from engine.scraping_sources.medium_scraper           import scrape_medium
from engine.scraping_sources.github_trending_scraper  import scrape_github_trending
from engine.scraping_sources.stackoverflow_scraper    import scrape_stackoverflow
from engine.scraping_sources.youtube_scraper          import scrape_youtube
from engine.scraping_sources.producthunt_scraper      import scrape_producthunt
from engine.scraping_sources.google_news_scraper      import scrape_google_news
from engine.scraping_sources.google_trends_scraper    import scrape_google_trends
from engine.scraping_sources.twitter_scraper          import scrape_twitter
from engine.scraping_sources.linkedin_scraper         import scrape_linkedin
from engine.scraping_sources.tiktok_scraper           import scrape_tiktok      # جديد
from engine.scraping_sources.instagram_scraper        import scrape_instagram    # جديد

logger = get_logger("ScrapingAgent")


class ScrapingAgent:

    def __init__(self, limit_per_source: int = 100):
        self.limit = limit_per_source
        self.sources = [
            scrape_reddit,
            scrape_hackernews,
            scrape_devto,
            scrape_medium,
            scrape_github_trending,
            scrape_stackoverflow,
            scrape_youtube,
            scrape_producthunt,
            scrape_google_news,
            scrape_google_trends,
            scrape_twitter,
            scrape_linkedin,
            scrape_tiktok,      # جديد
            scrape_instagram,   # جديد
        ]

    def collect_posts(self) -> list[dict]:
        logger.info(f"Starting parallel scraping ({len(self.sources)} sources)")
        posts = []

        with ThreadPoolExecutor(max_workers=14) as executor:
            futures = {
                executor.submit(source, self.limit): source.__name__
                for source in self.sources
            }
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    result = future.result(timeout=30)
                    posts.extend(result)
                    logger.info(f"{source_name} → {len(result)} posts")
                except Exception as e:
                    logger.error(f"{source_name} failed: {e}")

        logger.info(f"Total collected: {len(posts)} posts")
        return posts