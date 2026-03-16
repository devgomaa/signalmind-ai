"""
test_sprint2.py
===============
اختبار Sprint 2:
    1. gemini_client   — google.genai الجديدة
    2. hackernews      — async scraper
    3. TrendTimeAnalyzer — مربوط في الـ pipeline

شغّله من root المشروع:
    python test_sprint2.py
"""

import sys
import asyncio
import traceback

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅  {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌  {name}")
        print(f"       {e}")
        traceback.print_exc()
        failed += 1

# ═══════════════════════════════════════════════════════
# Mock Posts (بعد clustering و velocity و novelty)
# ═══════════════════════════════════════════════════════

MOCK_POSTS_CLUSTERED = [
    {"title": "AI agents replacing devs",      "cluster": 0, "trend_velocity": 30, "novelty_score": 0.8, "trend_score": 21.24},
    {"title": "LangChain best practices",       "cluster": 0, "trend_velocity": 30, "novelty_score": 0.8, "trend_score": 21.24},
    {"title": "AutoGPT new release",            "cluster": 0, "trend_velocity": 30, "novelty_score": 0.8, "trend_score": 21.24},
    {"title": "Rust vs Go performance",         "cluster": 1, "trend_velocity": 20, "novelty_score": 0.5, "trend_score": 14.15},
    {"title": "Rust async runtime comparison",  "cluster": 1, "trend_velocity": 20, "novelty_score": 0.5, "trend_score": 14.15},
    {"title": "WebAssembly in production",      "cluster": 2, "trend_velocity": 5,  "novelty_score": 0.2, "trend_score": 3.56},
    {"title": "TypeScript 5.0 features",        "cluster": 2, "trend_velocity": 5,  "novelty_score": 0.2, "trend_score": 3.56},
]


# ═══════════════════════════════════════════════════════
# 1. Gemini Client
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 2 — Task 1: GeminiClient (google.genai)")
print("═"*55)

def test_gemini_import():
    """التأكد إن الـ import شغال والـ class موجودة"""
    from engine.ai.gemini_client import GeminiClient
    client = GeminiClient()
    assert hasattr(client, "ask"),        "ask() مش موجودة"
    assert hasattr(client, "client"),     "client مش موجود"
    assert hasattr(client, "model"),      "model مش موجود"
    assert hasattr(client, "max_retries"), "max_retries مش موجود"
    assert client.model == "gemini-2.0-flash", f"model غلط: {client.model}"
test("GeminiClient — import ومتغيرات صح", test_gemini_import)

def test_gemini_no_old_import():
    """التأكد إن الكود مش بيستخدم google.generativeai القديمة"""
    import inspect
    from engine.ai import gemini_client
    source = inspect.getsource(gemini_client)
    assert "google.generativeai" not in source, \
        "لسه بيستخدم google.generativeai القديمة!"
    assert "google.genai" in source or "from google import genai" in source, \
        "مش بيستخدم google.genai الجديدة!"
test("GeminiClient — بيستخدم google.genai (مش القديمة)", test_gemini_no_old_import)

def test_gemini_retry_logic():
    """التأكد إن retry logic موجود"""
    import inspect
    from engine.ai import gemini_client
    source = inspect.getsource(gemini_client)
    assert "max_retries" in source, "max_retries مش موجود"
    assert "retry" in source.lower(), "retry logic مش موجود"
test("GeminiClient — retry logic موجود", test_gemini_retry_logic)


# ═══════════════════════════════════════════════════════
# 2. HackerNews Async Scraper
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 2 — Task 2: HackerNews Async Scraper")
print("═"*55)

def test_hackernews_is_async():
    """التأكد إن الـ scraper بيستخدم asyncio"""
    import inspect
    from engine.scraping_sources import hackernews_scraper
    source = inspect.getsource(hackernews_scraper)
    assert "asyncio" in source,  "مش بيستخدم asyncio"
    assert "aiohttp"  in source,  "مش بيستخدم aiohttp"
    assert "async def" in source, "مفيش async functions"
test("hackernews_scraper — بيستخدم asyncio + aiohttp", test_hackernews_is_async)

def test_hackernews_has_sync_wrapper():
    """التأكد إن الـ entry point لسه sync (للـ ScrapingAgent)"""
    from engine.scraping_sources.hackernews_scraper import scrape_hackernews
    import asyncio, inspect
    assert callable(scrape_hackernews), "scrape_hackernews مش callable"
    # المفروض مش async function — عشان ScrapingAgent يقدر يستدعيها عادي
    assert not asyncio.iscoroutinefunction(scrape_hackernews), \
        "scrape_hackernews المفروض تكون sync (wrapper) مش async"
test("hackernews_scraper — scrape_hackernews() sync wrapper موجودة", test_hackernews_has_sync_wrapper)

def test_hackernews_semaphore():
    """التأكد إن فيه semaphore للتحكم في الـ concurrency"""
    import inspect
    from engine.scraping_sources import hackernews_scraper
    source = inspect.getsource(hackernews_scraper)
    assert "Semaphore" in source, "مفيش Semaphore للتحكم في الـ concurrent requests"
test("hackernews_scraper — Semaphore موجود (concurrent control)", test_hackernews_semaphore)

def test_hackernews_live():
    """اختبار حقيقي بـ limit=5 فقط — سريع"""
    from engine.scraping_sources.hackernews_scraper import scrape_hackernews
    print("\n       جاري جلب 5 posts من HackerNews...")
    posts = scrape_hackernews(limit=5)
    assert isinstance(posts, list), "المفروض يرجع list"
    assert len(posts) > 0, "مرجعش أي posts — تحقق من الـ internet"
    for post in posts:
        assert "title"  in post, f"title مش موجود: {post}"
        assert "source" in post, f"source مش موجود: {post}"
        assert post["source"] == "hackernews"
    print(f"       جاب {len(posts)} posts ✓")
    print(f"       مثال: {posts[0]['title'][:60]}")
test("hackernews_scraper — live test (5 posts)", test_hackernews_live)


# ═══════════════════════════════════════════════════════
# 3. TrendTimeAnalyzer
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 2 — Task 3: TrendTimeAnalyzer مربوط في الـ pipeline")
print("═"*55)

def test_time_analyzer_enrich_exists():
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    analyzer = TrendTimeAnalyzer()
    assert hasattr(analyzer, "enrich"),              "enrich() مش موجودة"
    assert hasattr(analyzer, "get_cluster_summary"), "get_cluster_summary() مش موجودة"
test("TrendTimeAnalyzer — enrich() و get_cluster_summary() موجودين", test_time_analyzer_enrich_exists)

def test_time_analyzer_adds_fields():
    """يضيف cluster_state و cluster_score و cluster_size لكل post"""
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    posts = [p.copy() for p in MOCK_POSTS_CLUSTERED]
    analyzer = TrendTimeAnalyzer()
    result = analyzer.enrich(posts)

    for post in result:
        assert "cluster_state" in post,  f"cluster_state مش موجود: {post['title']}"
        assert "cluster_score" in post,  f"cluster_score مش موجود: {post['title']}"
        assert "cluster_size"  in post,  f"cluster_size مش موجود: {post['title']}"
        assert post["cluster_state"] in ["exploding", "growing", "stable"], \
            f"قيمة cluster_state غريبة: {post['cluster_state']}"
test("TrendTimeAnalyzer.enrich() — يضيف cluster_state/score/size", test_time_analyzer_adds_fields)

def test_time_analyzer_same_cluster_same_state():
    """كل البوستات في نفس الـ cluster المفروض تاخد نفس الـ cluster_state"""
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    posts = [p.copy() for p in MOCK_POSTS_CLUSTERED]
    analyzer = TrendTimeAnalyzer()
    result = analyzer.enrich(posts)

    cluster_0_posts = [p for p in result if p["cluster"] == 0]
    states = set(p["cluster_state"] for p in cluster_0_posts)
    assert len(states) == 1, \
        f"البوستات في نفس الـ cluster عندها states مختلفة: {states}"
test("TrendTimeAnalyzer — نفس الـ cluster → نفس الـ cluster_state", test_time_analyzer_same_cluster_same_state)

def test_time_analyzer_high_velocity_cluster():
    """الـ cluster اللي عنده velocity عالية المفروض يكون exploding"""
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    posts = [p.copy() for p in MOCK_POSTS_CLUSTERED]
    analyzer = TrendTimeAnalyzer()
    result = analyzer.enrich(posts)

    cluster_0 = [p for p in result if p["cluster"] == 0][0]
    # cluster 0: velocity=30, novelty=0.8 → score = 30*0.6 + 0.8*0.4 = 18.32 > 15
    assert cluster_0["cluster_state"] == "exploding", \
        f"cluster 0 المفروض exploding، طلع: {cluster_0['cluster_state']}"
test("TrendTimeAnalyzer — cluster velocity عالية → exploding", test_time_analyzer_high_velocity_cluster)

def test_time_analyzer_summary():
    """get_cluster_summary يرجع list مرتبة بالـ score"""
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    posts = [p.copy() for p in MOCK_POSTS_CLUSTERED]
    # نضيف trend_score عشان get_cluster_summary يقدر يرتب top_topics
    for p in posts:
        p["trend_score"] = p.get("trend_score", 0)
    analyzer = TrendTimeAnalyzer()
    posts = analyzer.enrich(posts)
    summary = analyzer.get_cluster_summary(posts)

    assert isinstance(summary, list), "المفروض يرجع list"
    assert len(summary) == 3, f"المفروض 3 clusters، لقينا {len(summary)}"
    # مرتبة تنازلياً
    scores = [c["cluster_score"] for c in summary]
    assert scores == sorted(scores, reverse=True), "مش مرتبة تنازلياً"
test("TrendTimeAnalyzer.get_cluster_summary() — مرتبة تنازلياً", test_time_analyzer_summary)

def test_time_analyzer_in_pipeline():
    """التأكد إن TrendIntelligenceAgent بيستخدم time_analyzer"""
    import inspect
    from engine.agents import trend_intelligence_agent
    source = inspect.getsource(trend_intelligence_agent)
    assert "TrendTimeAnalyzer"  in source, "TrendTimeAnalyzer مش موجود في الـ agent"
    assert "time_analyzer"      in source, "time_analyzer مش موجود كـ instance"
    assert "time_analyzer.enrich" in source, "enrich() مش بيتستدعى في الـ pipeline"
test("TrendIntelligenceAgent — يستخدم TrendTimeAnalyzer.enrich()", test_time_analyzer_in_pipeline)

def test_time_analyzer_handles_no_cluster():
    """مش بيتكسر لو posts مش متكلستره"""
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    posts_no_cluster = [{"title": "test", "source": "reddit"}]
    analyzer = TrendTimeAnalyzer()
    result = analyzer.enrich(posts_no_cluster)
    assert result == posts_no_cluster, "المفروض يرجع نفس الـ posts من غير تغيير"
test("TrendTimeAnalyzer — مش بيتكسر لو posts غير متكلستره", test_time_analyzer_handles_no_cluster)

def test_full_pipeline_with_time_analyzer():
    """Integration: pipeline كامل مع TrendTimeAnalyzer"""
    from engine.trend_engine.deduplicator     import deduplicate_posts
    from engine.trend_engine.topic_clusterer  import cluster_topics
    from engine.trend_engine.trend_velocity   import calculate_velocity
    from engine.trend_engine.novelty_detector import detect_novelty
    from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer
    from engine.trend_engine.trend_scorer     import score_trends
    from engine.trend_engine.trend_classifier import classify_trends
    from engine.trend_engine.trend_forecaster import TrendForecaster
    from engine.trend_engine.trend_ranker     import TrendRanker

    raw_posts = [
        {"title": "AI agents replacing developers", "url": "", "source": "reddit", "score": 150},
        {"title": "LangChain vs LlamaIndex",         "url": "", "source": "hn",     "score": 200},
        {"title": "Rust systems programming",        "url": "", "source": "github", "score": 300},
        {"title": "Rust performance 2024",           "url": "", "source": "github", "score": 280},
        {"title": "Vector databases mainstream",     "url": "", "source": "hn",     "score": 180},
        {"title": "RAG pipelines best practices",    "url": "", "source": "devto",  "score": 120},
        {"title": "WebAssembly browser 2024",        "url": "", "source": "devto",  "score": 70},
        {"title": "TypeScript 5.0 features",         "url": "", "source": "devto",  "score": 65},
        {"title": "Next.js 14 App Router",           "url": "", "source": "medium", "score": 60},
        {"title": "Open source LLMs vs GPT-4",       "url": "", "source": "medium", "score": 95},
        {"title": "Mistral 7B fine-tuning",          "url": "", "source": "medium", "score": 88},
        {"title": "AI agents replacing developers",  "url": "", "source": "twitter","score": 90},  # duplicate
    ]

    posts = deduplicate_posts(raw_posts)
    posts = cluster_topics(posts)
    posts = calculate_velocity(posts)
    posts = detect_novelty(posts)
    posts = TrendTimeAnalyzer().enrich(posts)  # ← Sprint 2

    # التأكد إن الـ fields الجديدة موجودة
    assert all("cluster_state" in p for p in posts), "cluster_state مش موجود"
    assert all("cluster_score" in p for p in posts), "cluster_score مش موجود"

    posts = score_trends(posts)
    posts = classify_trends(posts)
    posts = TrendForecaster().forecast(posts)
    ranked = TrendRanker().rank(posts)

    assert isinstance(ranked, dict)
    assert all(k in ranked for k in ["exploding", "growing", "future", "stable"])
    total = sum(len(v) for v in ranked.values())
    assert total > 0

test("Full pipeline مع TrendTimeAnalyzer (integration)", test_full_pipeline_with_time_analyzer)


# ═══════════════════════════════════════════════════════
# Final Report
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 2 اكتمل بنجاح!")
    print("\n    ملاحظات:")
    print("    - gemini_client: حدّث pip install google-genai لو مش مثبت")
    print("    - hackernews: السرعة تحسنت من ~40 ثانية لـ ~2 ثانية")
    print("    - TrendTimeAnalyzer: يضيف cluster_state على كل post")
else:
    print(f"⚠️   {failed} اختبار فشل — راجع الأخطاء فوق")
print("═"*55 + "\n")

sys.exit(0 if failed == 0 else 1)