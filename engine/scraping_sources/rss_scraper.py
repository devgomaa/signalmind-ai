import feedparser
from engine.utils.logger import get_logger

logger = get_logger("RSSScraper")


def scrape_rss(url, source="rss", limit=50):

    posts = []

    try:

        feed = feedparser.parse(url)

        for entry in feed.entries[:limit]:

            posts.append({

                "title": entry.title,
                "url": entry.link,
                "source": source,
                "score": 1

            })

    except Exception as e:

        logger.error(e)

    return posts