"""engine/scraping_sources/youtube_scraper.py — Sprint 4"""
from engine.scraping_sources.base_scraper import BaseScraper

# channels تقنية معروفة
CHANNELS = {
    "UC_x5XG1OV2P6uZZ5FSM9Ttw": "Google Developers",
    "UCnUYZLuoy1rq1aVMwx4aTzw":  "Google Cloud",
    "UCVHFbw7woebKtX3KiNIOJiA":  "Fireship",
    "UCsBjURrPoezykLs9EqgamOA":  "Fireship (alt)",
}


class YouTubeScraper(BaseScraper):
    SOURCE_NAME = "youtube"

    def fetch(self, limit: int = 50) -> list[dict]:
        posts = []
        seen  = set()
        per_ch = max(limit // len(CHANNELS), 5)

        for channel_id in CHANNELS:
            entries = self.get_feed(
                f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            )
            for entry in entries[:per_ch]:
                title = getattr(entry, "title", "").strip()
                url   = getattr(entry, "link",  "")
                if title and title not in seen:
                    seen.add(title)
                    post = self.make_post(title, url, "youtube", 1)
                    if post:
                        posts.append(post)
            if len(posts) >= limit:
                break

        self.logger.info(f"YouTube returned {len(posts)} posts")
        return posts[:limit]


def scrape_youtube(limit: int = 50) -> list[dict]:
    return YouTubeScraper().fetch(limit)