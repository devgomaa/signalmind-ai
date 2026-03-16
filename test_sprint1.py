"""
test_sprint1.py
===============
اختبار كل Bug Fixes من Sprint 1 بدون Gemini API ومن غير internet.
شغّله من root المشروع:
    python test_sprint1.py
"""

import sys
import traceback

# ═══════════════════════════════════════════════════════
# Mock Data — بوستات وهمية لتجربة الـ pipeline
# ═══════════════════════════════════════════════════════

MOCK_POSTS = [
    {"title": "AI agents are replacing junior developers", "url": "https://reddit.com/1", "source": "reddit", "score": 150},
    {"title": "AI agents are replacing junior developers", "url": "https://reddit.com/2", "source": "reddit", "score": 90},   # duplicate
    {"title": "LangChain vs LlamaIndex comparison 2024",  "url": "https://hn.com/1",     "source": "hackernews", "score": 200},
    {"title": "Vector databases becoming mainstream",      "url": "https://hn.com/2",     "source": "hackernews", "score": 180},
    {"title": "RAG pipelines best practices",              "url": "https://devto.com/1",  "source": "devto",      "score": 120},
    {"title": "Rust is taking over systems programming",   "url": "https://gh.com/1",     "source": "github",     "score": 300},
    {"title": "Rust performance benchmarks 2024",          "url": "https://gh.com/2",     "source": "github",     "score": 280},
    {"title": "Rust vs Go for backend services",           "url": "https://gh.com/3",     "source": "github",     "score": 260},
    {"title": "Open source LLMs catching up to GPT-4",    "url": "https://medium.com/1", "source": "medium",     "score": 95},
    {"title": "Mistral 7B fine-tuning guide",              "url": "https://medium.com/2", "source": "medium",     "score": 88},
    {"title": "WebAssembly in the browser in 2024",        "url": "https://devto.com/2",  "source": "devto",      "score": 70},
    {"title": "TypeScript 5.0 new features",               "url": "https://devto.com/3",  "source": "devto",      "score": 65},
    {"title": "Next.js 14 App Router deep dive",           "url": "https://devto.com/4",  "source": "devto",      "score": 60},
    {"title": "",                                          "url": "https://empty.com",    "source": "test",       "score": 0},   # empty title
    {"title": "   ",                                       "url": "https://space.com",    "source": "test",       "score": 0},   # whitespace title
]

MOCK_RANKED = {
    "exploding": [
        {"title": "Rust is taking over systems programming", "trend_score": 25.0, "trend_state": "exploding"},
        {"title": "AI agents are replacing junior developers", "trend_score": 22.0, "trend_state": "exploding"},
    ],
    "growing": [
        {"title": "Vector databases becoming mainstream", "trend_score": 14.0, "trend_state": "growing"},
        {"title": "RAG pipelines best practices",         "trend_score": 11.0, "trend_state": "growing"},
    ],
    "future": [
        {"title": "Open source LLMs catching up to GPT-4", "trend_score": 8.0, "trend_state": "stable", "forecast": "future_trend"},
    ],
    "stable": [
        {"title": "TypeScript 5.0 new features", "trend_score": 3.0, "trend_state": "stable"},
    ]
}

# ═══════════════════════════════════════════════════════
# Test Runner
# ═══════════════════════════════════════════════════════

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
# Bug #1 — Function Names
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #1 — Function name mismatch")
print("═"*55)

def test_deduplicator_name():
    from engine.trend_engine.deduplicator import deduplicate_posts
    result = deduplicate_posts(MOCK_POSTS)
    assert callable(deduplicate_posts), "deduplicate_posts غير موجودة"
    assert len(result) < len(MOCK_POSTS), "مش شايل duplicates"
test("deduplicator — deduplicate_posts موجودة", test_deduplicator_name)

def test_deduplicator_removes_duplicates():
    from engine.trend_engine.deduplicator import deduplicate_posts
    result = deduplicate_posts(MOCK_POSTS)
    titles = [p["title"] for p in result]
    assert len(titles) == len(set(titles)), "في duplicates لسه موجودة"
    # التأكد إن الـ empty titles اتشالت
    assert all(t.strip() for t in titles), "في empty titles لسه موجودة"
test("deduplicator — يشيل duplicates وempty titles", test_deduplicator_removes_duplicates)

def test_velocity_name():
    from engine.trend_engine.trend_velocity import calculate_velocity
    assert callable(calculate_velocity), "calculate_velocity غير موجودة"
test("trend_velocity — calculate_velocity موجودة", test_velocity_name)

def test_novelty_name():
    from engine.trend_engine.novelty_detector import detect_novelty
    assert callable(detect_novelty), "detect_novelty غير موجودة"
test("novelty_detector — detect_novelty موجودة", test_novelty_name)

def test_scorer_name():
    from engine.trend_engine.trend_scorer import score_trends
    assert callable(score_trends), "score_trends غير موجودة"
test("trend_scorer — score_trends موجودة", test_scorer_name)

def test_old_aliases_still_work():
    from engine.trend_engine.deduplicator  import remove_duplicates
    from engine.trend_engine.trend_velocity import compute_velocity
    from engine.trend_engine.novelty_detector import compute_novelty
    from engine.trend_engine.trend_scorer import compute_trend_score
    assert callable(remove_duplicates)
    assert callable(compute_velocity)
    assert callable(compute_novelty)
    assert callable(compute_trend_score)
test("aliases القديمة لسه شغالة (backward compat)", test_old_aliases_still_work)


# ═══════════════════════════════════════════════════════
# Bug #2 — analyze() alias
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #2 — TrendIntelligenceAgent.analyze() missing")
print("═"*55)

def test_analyze_method_exists():
    from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
    agent = TrendIntelligenceAgent()
    assert hasattr(agent, "analyze"),       "analyze() مش موجودة"
    assert hasattr(agent, "detect_trends"), "detect_trends() مش موجودة"
test("TrendIntelligenceAgent — analyze() و detect_trends() موجودين", test_analyze_method_exists)

def test_analyze_same_as_detect():
    from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
    agent = TrendIntelligenceAgent()
    # التأكد إن الاتنين بيرجعوا نفس النوع
    import inspect
    src_analyze      = inspect.getsource(agent.analyze)
    src_detect       = inspect.getsource(agent.detect_trends)
    # analyze المفروض تستدعي detect_trends
    assert "detect_trends" in src_analyze, "analyze() مش بتستدعي detect_trends()"
test("analyze() هي alias حقيقية لـ detect_trends()", test_analyze_same_as_detect)


# ═══════════════════════════════════════════════════════
# Bug #3 — expand_topics()
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #3 — DeepSearchAgent.expand_topics() missing")
print("═"*55)

def test_expand_topics_exists():
    from engine.agents.deep_search_agent import DeepSearchAgent
    agent = DeepSearchAgent()
    assert hasattr(agent, "expand_topics"),  "expand_topics() مش موجودة"
    assert hasattr(agent, "discover_trends"), "discover_trends() مش موجودة"
test("DeepSearchAgent — expand_topics() و discover_trends() موجودين", test_expand_topics_exists)

def test_expand_topics_extends_list():
    """نختبر expand_topics بـ mock بدون Gemini"""
    from engine.agents.deep_search_agent import DeepSearchAgent

    agent = DeepSearchAgent()
    original_discover = agent.discover_trends

    # Mock — بدل ما يكلم Gemini
    agent.discover_trends = lambda: [
        {"title": "Mock trend 1", "url": "", "source": "deep_search", "score": 1},
        {"title": "Mock trend 2", "url": "", "source": "deep_search", "score": 1},
    ]

    posts = [{"title": "Existing post", "url": "", "source": "reddit", "score": 5}]
    result = agent.expand_topics(posts)

    assert len(result) == 3, f"المفروض 3 posts، لقينا {len(result)}"
    sources = [p["source"] for p in result]
    assert "deep_search" in sources, "الـ deep_search posts مش اتضافت"

    agent.discover_trends = original_discover  # restore
test("expand_topics() تضيف trends على posts الموجودة", test_expand_topics_extends_list)


# ═══════════════════════════════════════════════════════
# Bug #4 — generate() aliases
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #4 — generate() aliases missing in agents")
print("═"*55)

def test_strategy_generate_exists():
    from engine.agents.content_strategy_agent import ContentStrategyAgent
    agent = ContentStrategyAgent()
    assert hasattr(agent, "generate"),          "generate() مش موجودة"
    assert hasattr(agent, "generate_strategy"), "generate_strategy() مش موجودة"
test("ContentStrategyAgent — generate() و generate_strategy() موجودين", test_strategy_generate_exists)

def test_content_generate_exists():
    from engine.agents.content_generation_agent import ContentGenerationAgent
    agent = ContentGenerationAgent()
    assert hasattr(agent, "generate"),       "generate() مش موجودة"
    assert hasattr(agent, "generate_posts"), "generate_posts() مش موجودة"
test("ContentGenerationAgent — generate() و generate_posts() موجودين", test_content_generate_exists)


# ═══════════════════════════════════════════════════════
# Bug #5 — trend_state vs trend_type
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #5 — trend_type vs trend_state field name")
print("═"*55)

def test_classifier_writes_trend_state():
    from engine.trend_engine.trend_classifier import classify_trends

    posts = [
        {"title": "High score post",  "trend_score": 25},
        {"title": "Mid score post",   "trend_score": 15},
        {"title": "Low score post",   "trend_score": 5},
    ]
    result = classify_trends(posts)

    for post in result:
        assert "trend_state" in post,     f"trend_state مش موجود في: {post['title']}"
        assert "trend_type" not in post,  f"trend_type لسه موجود (القديم) في: {post['title']}"
        assert post["trend_state"] in ["exploding", "growing", "stable"], \
            f"قيمة غريبة: {post['trend_state']}"
test("trend_classifier — يكتب trend_state (مش trend_type)", test_classifier_writes_trend_state)

def test_classifier_thresholds():
    from engine.trend_engine.trend_classifier import classify_trends

    posts = [
        {"title": "A", "trend_score": 21},
        {"title": "B", "trend_score": 11},
        {"title": "C", "trend_score": 5},
    ]
    result = classify_trends(posts)
    assert result[0]["trend_state"] == "exploding", f"المفروض exploding، طلع {result[0]['trend_state']}"
    assert result[1]["trend_state"] == "growing",   f"المفروض growing، طلع {result[1]['trend_state']}"
    assert result[2]["trend_state"] == "stable",    f"المفروض stable، طلع {result[2]['trend_state']}"
test("trend_classifier — thresholds صح (>20 exploding, >10 growing)", test_classifier_thresholds)

def test_forecaster_reads_trend_state():
    from engine.trend_engine.trend_forecaster import TrendForecaster

    posts = [
        {"title": "Viral post",   "trend_score": 25, "trend_state": "exploding"},
        {"title": "Future post",  "trend_score": 14, "trend_state": "growing"},
        {"title": "Stable post",  "trend_score": 5,  "trend_state": "stable"},
    ]
    forecaster = TrendForecaster()
    result = forecaster.forecast(posts)

    assert result[0]["forecast"] == "viral",        f"المفروض viral، طلع {result[0]['forecast']}"
    assert result[1]["forecast"] == "future_trend", f"المفروض future_trend، طلع {result[1]['forecast']}"
    assert result[2]["forecast"] == "stable",       f"المفروض stable، طلع {result[2]['forecast']}"
test("TrendForecaster — يقرأ trend_state صح ويولد forecast صح", test_forecaster_reads_trend_state)

def test_ranker_reads_trend_state():
    from engine.trend_engine.trend_ranker import TrendRanker

    posts = [
        {"title": "A", "trend_score": 25, "trend_state": "exploding", "forecast": "viral"},
        {"title": "B", "trend_score": 14, "trend_state": "growing",   "forecast": "stable"},
        {"title": "C", "trend_score": 8,  "trend_state": "stable",    "forecast": "future_trend"},
        {"title": "D", "trend_score": 3,  "trend_state": "stable",    "forecast": "stable"},
    ]
    ranker = TrendRanker()
    result = ranker.rank(posts)

    assert isinstance(result, dict), "الـ output مش dict"
    assert "exploding" in result and "growing" in result and "future" in result and "stable" in result
    assert len(result["exploding"]) == 1, f"المفروض 1 exploding، لقينا {len(result['exploding'])}"
    assert len(result["growing"])   == 1, f"المفروض 1 growing، لقينا {len(result['growing'])}"
    assert len(result["future"])    == 1, f"المفروض 1 future، لقينا {len(result['future'])}"
    assert result["exploding"][0]["title"] == "A"
test("TrendRanker — يصنف في 4 buckets صح", test_ranker_reads_trend_state)


# ═══════════════════════════════════════════════════════
# Bug #6 — ContentStrategyAgent handles ranked dict
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Bug #6 — ContentStrategyAgent يتعامل مع ranked dict")
print("═"*55)

def test_flatten_dict_input():
    from engine.agents.content_strategy_agent import ContentStrategyAgent
    agent = ContentStrategyAgent()

    flat = agent._flatten_trends(MOCK_RANKED)
    assert isinstance(flat, list), "المفروض يرجع list"
    assert len(flat) > 0, "الـ list فاضية"
    # التأكد إن exploding جت أول
    assert flat[0]["trend_state"] == "exploding", "exploding مش أول في الترتيب"
test("ContentStrategyAgent._flatten_trends() — تحوّل dict لـ list بالترتيب الصح", test_flatten_dict_input)

def test_flatten_list_input():
    from engine.agents.content_strategy_agent import ContentStrategyAgent
    agent = ContentStrategyAgent()

    input_list = [{"title": "T1"}, {"title": "T2"}]
    result = agent._flatten_trends(input_list)
    assert result == input_list, "لما الـ input list ترجعها كما هي"
test("ContentStrategyAgent._flatten_trends() — تقبل list كمان", test_flatten_list_input)

def test_topics_extraction_safe():
    """التأكد إن مفيش KeyError لو title مش موجود"""
    from engine.agents.content_strategy_agent import ContentStrategyAgent
    agent = ContentStrategyAgent()

    bad_trends = {
        "exploding": [{"trend_score": 10, "trend_state": "exploding"}],  # no title
        "growing": [], "future": [], "stable": []
    }
    flat = agent._flatten_trends(bad_trends)
    assert isinstance(flat, list)
test("ContentStrategyAgent — مش بتتكسر لو post مفيهوش title", test_topics_extraction_safe)


# ═══════════════════════════════════════════════════════
# Integration Test — Pipeline كامل بـ mock data
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Integration — Pipeline كامل بـ mock (بدون API)")
print("═"*55)

def test_full_trend_pipeline_no_api():
    """
    تشغيل trend engine كامل من deduplicate حتى rank
    بدون أي API calls.
    """
    from engine.trend_engine.deduplicator   import deduplicate_posts
    from engine.trend_engine.topic_clusterer import cluster_topics
    from engine.trend_engine.trend_velocity  import calculate_velocity
    from engine.trend_engine.novelty_detector import detect_novelty
    from engine.trend_engine.trend_scorer    import score_trends
    from engine.trend_engine.trend_classifier import classify_trends
    from engine.trend_engine.trend_forecaster import TrendForecaster
    from engine.trend_engine.trend_ranker    import TrendRanker

    posts = MOCK_POSTS.copy()

    posts = deduplicate_posts(posts)
    assert len(posts) > 0

    posts = cluster_topics(posts)
    assert all("cluster" in p for p in posts)

    posts = calculate_velocity(posts)
    assert all("trend_velocity" in p for p in posts)

    posts = detect_novelty(posts)
    assert all("novelty_score" in p for p in posts)

    posts = score_trends(posts)
    assert all("trend_score" in p for p in posts)

    posts = classify_trends(posts)
    assert all("trend_state" in p for p in posts)
    assert all("trend_type" not in p for p in posts), "trend_type لسه موجود!"

    posts = TrendForecaster().forecast(posts)
    assert all("forecast" in p for p in posts)

    ranked = TrendRanker().rank(posts)
    assert isinstance(ranked, dict)
    assert all(k in ranked for k in ["exploding", "growing", "future", "stable"])

    total = sum(len(v) for v in ranked.values())
    assert total > 0, "مفيش ترندات في الـ output"

test("Full trend pipeline (dedupe → cluster → velocity → novelty → score → classify → forecast → rank)", test_full_trend_pipeline_no_api)


# ═══════════════════════════════════════════════════════
# Final Report
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  كل Sprint 1 bugs اتصلحت بنجاح!")
else:
    print(f"⚠️   {failed} اختبار فشل — راجع الأخطاء فوق")
print("═"*55 + "\n")

sys.exit(0 if failed == 0 else 1)