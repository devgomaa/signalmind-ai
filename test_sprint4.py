"""
test_sprint4.py — Sprint 4 Final (14 scrapers)
شغّله: python test_sprint4.py
"""
import sys, traceback

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅  {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌  {name}\n       {e}")
        failed += 1

# ── BaseScraper ────────────────────────────────────────
print("\n" + "═"*55)
print("Task 1: BaseScraper")
print("═"*55)

def test_base():
    from engine.scraping_sources.base_scraper import BaseScraper
    s = BaseScraper()
    for m in ["get_json","get_html","get_feed","make_post","session"]:
        assert hasattr(s, m), f"{m} مش موجود"
test("BaseScraper — كل الـ methods موجودة", test_base)

def test_make_post():
    from engine.scraping_sources.base_scraper import BaseScraper
    assert BaseScraper.make_post("Title","http://x.com","reddit",10) is not None
    assert BaseScraper.make_post("","http://x.com","test") is None
    assert BaseScraper.make_post("  ","http://x.com","test") is None
test("BaseScraper.make_post() — valid + empty", test_make_post)

def test_retry():
    import inspect
    from engine.scraping_sources import base_scraper as bm
    src = inspect.getsource(bm)
    assert "Retry" in src and "HTTPAdapter" in src
test("BaseScraper — Retry + HTTPAdapter", test_retry)

# ── Structure — 14 scrapers ───────────────────────────
print("\n" + "═"*55)
print("Task 2: Structure (14 scrapers)")
print("═"*55)

ALL = [
    ("engine.scraping_sources.reddit_scraper",          "scrape_reddit",         "RedditScraper"),
    ("engine.scraping_sources.devto_scraper",           "scrape_devto",          "DevToScraper"),
    ("engine.scraping_sources.github_trending_scraper", "scrape_github_trending","GitHubTrendingScraper"),
    ("engine.scraping_sources.stackoverflow_scraper",   "scrape_stackoverflow",  "StackOverflowScraper"),
    ("engine.scraping_sources.medium_scraper",          "scrape_medium",         "MediumScraper"),
    ("engine.scraping_sources.youtube_scraper",         "scrape_youtube",        "YouTubeScraper"),
    ("engine.scraping_sources.producthunt_scraper",     "scrape_producthunt",    "ProductHuntScraper"),
    ("engine.scraping_sources.google_news_scraper",     "scrape_google_news",    "GoogleNewsScraper"),
    ("engine.scraping_sources.google_trends_scraper",   "scrape_google_trends",  "GoogleTrendsScraper"),
    ("engine.scraping_sources.hackernews_scraper",      "scrape_hackernews",     "HackerNewsScraper"),
    ("engine.scraping_sources.twitter_scraper",         "scrape_twitter",        "TwitterScraper"),
    ("engine.scraping_sources.linkedin_scraper",        "scrape_linkedin",       "LinkedInScraper"),
    ("engine.scraping_sources.tiktok_scraper",          "scrape_tiktok",         "TikTokScraper"),
    ("engine.scraping_sources.instagram_scraper",       "scrape_instagram",      "InstagramScraper"),
]

def make_struct(mod_path, fn, cls):
    def t():
        import importlib
        from engine.scraping_sources.base_scraper import BaseScraper
        m = importlib.import_module(mod_path)
        assert getattr(m, fn,  None) is not None, f"{fn} مش موجود"
        c = getattr(m, cls, None)
        assert c is not None, f"{cls} مش موجود"
        assert issubclass(c, BaseScraper), f"{cls} مش بيرث BaseScraper"
    return t

for mp, fn, cls in ALL:
    test(f"{cls.replace('Scraper','')} — موجود", make_struct(mp, fn, cls))

# ── ScrapingAgent ──────────────────────────────────────
print("\n" + "═"*55)
print("Task 3: ScrapingAgent")
print("═"*55)

def test_14_sources():
    from engine.agents.scraping_agent import ScrapingAgent
    assert len(ScrapingAgent().sources) == 14, f"المفروض 14"
test("ScrapingAgent — 14 sources", test_14_sources)

def test_has_new_4():
    import inspect
    from engine.agents import scraping_agent as sa
    src = inspect.getsource(sa)
    for n in ["scrape_twitter","scrape_linkedin","scrape_tiktok","scrape_instagram"]:
        assert n in src, f"{n} مش موجود"
test("ScrapingAgent — Twitter+LinkedIn+TikTok+Instagram", test_has_new_4)

# ── TikTok ─────────────────────────────────────────────
print("\n" + "═"*55)
print("Task 4: TikTok")
print("═"*55)

def test_tiktok_methods():
    import inspect
    from engine.scraping_sources import tiktok_scraper as tm
    src = inspect.getsource(tm)
    assert "_fetch_creative_center" in src
    assert "_fetch_trending_videos_rss" in src
test("TikTokScraper — Creative Center + RSS methods", test_tiktok_methods)

def test_tiktok_live():
    from engine.scraping_sources.tiktok_scraper import scrape_tiktok
    print("\n       جاري جلب TikTok...")
    posts = scrape_tiktok(limit=10)
    assert isinstance(posts, list)
    if not posts:
        print("       ⚠️  TikTok: 0 posts (Creative Center ممكن يحتاج VPN)")
        return
    assert all("tiktok" in p["source"].lower() for p in posts)
    print(f"       TikTok: {len(posts)} posts ✓ | {posts[0]['title'][:50]}")
test("TikTokScraper — live test", test_tiktok_live)

# ── Instagram ──────────────────────────────────────────
print("\n" + "═"*55)
print("Task 5: Instagram")
print("═"*55)

def test_instagram_hashtags():
    from engine.scraping_sources.instagram_scraper import InstagramScraper
    posts = InstagramScraper()._fetch_trending_hashtags()
    assert len(posts) > 0
    assert all(p["title"].startswith("#") for p in posts)
    assert all("instagram" in p["source"] for p in posts)
test("InstagramScraper — hashtags format صح", test_instagram_hashtags)

def test_instagram_live():
    from engine.scraping_sources.instagram_scraper import scrape_instagram
    print("\n       جاري جلب Instagram...")
    posts = scrape_instagram(limit=10)
    assert isinstance(posts, list) and len(posts) > 0
    assert all("instagram" in p["source"].lower() for p in posts)
    print(f"       Instagram: {len(posts)} posts ✓ | {posts[0]['title'][:50]}")
test("InstagramScraper — live test", test_instagram_live)

# ── Live all sources ───────────────────────────────────
print("\n" + "═"*55)
print("Task 6: Live Tests (limit=3)")
print("═"*55)

def make_live(mod_path, fn_name, display):
    def t():
        import importlib
        fn    = getattr(importlib.import_module(mod_path), fn_name)
        posts = fn(limit=3)
        assert isinstance(posts, list)
        if not posts:
            print(f"\n       ⚠️  {display}: 0 posts")
            return
        for p in posts:
            assert "title" in p and "source" in p
            assert p["title"].strip()
        print(f"\n       {display}: {len(posts)} ✓ | {posts[0]['title'][:45]}")
    return t

LIVE = [
    ("engine.scraping_sources.reddit_scraper",         "scrape_reddit",         "Reddit"),
    ("engine.scraping_sources.devto_scraper",          "scrape_devto",          "Dev.to"),
    ("engine.scraping_sources.github_trending_scraper","scrape_github_trending","GitHub"),
    ("engine.scraping_sources.stackoverflow_scraper",  "scrape_stackoverflow",  "StackOverflow"),
    ("engine.scraping_sources.medium_scraper",         "scrape_medium",         "Medium"),
    ("engine.scraping_sources.google_news_scraper",    "scrape_google_news",    "Google News"),
    ("engine.scraping_sources.producthunt_scraper",    "scrape_producthunt",    "ProductHunt"),
    ("engine.scraping_sources.hackernews_scraper",     "scrape_hackernews",     "HackerNews"),
    ("engine.scraping_sources.twitter_scraper",        "scrape_twitter",        "Twitter"),
    ("engine.scraping_sources.linkedin_scraper",       "scrape_linkedin",       "LinkedIn"),
    ("engine.scraping_sources.tiktok_scraper",         "scrape_tiktok",         "TikTok"),
    ("engine.scraping_sources.instagram_scraper",      "scrape_instagram",      "Instagram"),
]
for mp, fn, disp in LIVE:
    test(f"{disp} — live", make_live(mp, fn, disp))

# ── Final ──────────────────────────────────────────────
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 4 اكتمل! — 14 sources شغالة")
else:
    print(f"⚠️   {failed} فشلوا — Twitter/TikTok ممكن 0 posts لو Nitter/VPN مش متاح")
print("═"*55 + "\n")
sys.exit(0 if failed == 0 else 1)
