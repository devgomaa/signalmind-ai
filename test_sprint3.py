"""
test_sprint3.py
===============
اختبار Sprint 3: Config + Database
شغّله من root المشروع:
    python test_sprint3.py
"""

import sys
import os
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

# DB مؤقت للتجارب — مش هيأثر على الـ production DB
TEST_DB_PATH = "data/db/test_sprint3.db"


# ═══════════════════════════════════════════════════════
# 1. Config
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 1: Config")
print("═"*55)

def test_config_has_db_path():
    from engine.config import Config
    assert hasattr(Config, "DATABASE_PATH"), "DATABASE_PATH مش موجود"
    assert "db" in Config.DATABASE_PATH or ".db" in Config.DATABASE_PATH, \
        f"DATABASE_PATH يبدو غريب: {Config.DATABASE_PATH}"
test("Config — DATABASE_PATH موجود", test_config_has_db_path)

def test_config_ensure_dirs():
    from engine.config import Config
    Config.ensure_dirs()
    assert os.path.exists("data/raw"),       "data/raw مش موجود"
    assert os.path.exists("data/processed"), "data/processed مش موجود"
    assert os.path.exists("data/db"),        "data/db مش موجود"
test("Config.ensure_dirs() — ينشئ الـ directories", test_config_ensure_dirs)

def test_config_validate_missing_key():
    """لو GEMINI_API_KEY مش موجود المفروض يرمي error"""
    from engine.config import Config
    original = Config.GEMINI_API_KEY
    Config.GEMINI_API_KEY = None
    try:
        Config.validate()
        assert False, "المفروض رمى EnvironmentError"
    except EnvironmentError:
        pass  # ده المتوقع
    finally:
        Config.GEMINI_API_KEY = original
test("Config.validate() — يرمي error لو API key ناقص", test_config_validate_missing_key)

def test_config_scraping_limit():
    from engine.config import Config
    assert isinstance(Config.SCRAPING_LIMIT, int), "SCRAPING_LIMIT مش int"
    assert Config.SCRAPING_LIMIT > 0, "SCRAPING_LIMIT لازم > 0"
test("Config — SCRAPING_LIMIT صح", test_config_scraping_limit)


# ═══════════════════════════════════════════════════════
# 2. Database Models
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 2: Database Models")
print("═"*55)

def test_models_import():
    from engine.database.models import Post, Trend, Content, PipelineRun
    p = Post(title="Test", source="reddit")
    assert p.title == "Test"
    assert p.source == "reddit"
    assert p.score == 0
    assert p.id is None
    assert p.created_at != ""
test("Models — Post dataclass صح", test_models_import)

def test_trend_model():
    from engine.database.models import Trend
    t = Trend(cluster_id=1, cluster_state="exploding",
              cluster_score=18.5, top_topics="[]", keywords="[]", post_count=3)
    assert t.cluster_state == "exploding"
    assert t.forecast == "stable"  # default
test("Models — Trend dataclass صح", test_trend_model)

def test_pipeline_run_model():
    from engine.database.models import PipelineRun
    r = PipelineRun()
    assert r.status == "running"
    assert r.posts_count == 0
test("Models — PipelineRun dataclass صح", test_pipeline_run_model)


# ═══════════════════════════════════════════════════════
# 3. DatabaseManager — Tables
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 3: DatabaseManager — Tables")
print("═"*55)

def test_db_creates_tables():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    import sqlite3
    conn = sqlite3.connect(TEST_DB_PATH)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    table_names = {t[0] for t in tables}
    for expected in ["posts", "trends", "content", "pipeline_runs"]:
        assert expected in table_names, f"table '{expected}' مش موجودة"
test("DatabaseManager — ينشئ الـ 4 tables", test_db_creates_tables)

def test_db_idempotent():
    """create_tables المفروض تشتغل أكتر من مرة بدون error"""
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    db.create_tables()
    db.create_tables()
test("DatabaseManager — create_tables idempotent", test_db_idempotent)


# ═══════════════════════════════════════════════════════
# 4. PipelineRun CRUD
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 4: PipelineRun CRUD")
print("═"*55)

def test_start_and_finish_run():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    assert run_id is not None
    assert isinstance(run_id, str)

    db.finish_run(run_id, posts_count=100, trends_count=10, duration_sec=5.2)
    runs = db.get_runs(limit=1)
    assert len(runs) > 0
    latest = runs[0]
    assert latest["status"] == "completed"
    assert latest["posts_count"] == 100
    assert latest["duration_sec"] == 5.2
test("PipelineRun — start_run() و finish_run() شغالين", test_start_and_finish_run)

def test_failed_run():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    db.finish_run(run_id, 0, 0, 1.0, error="Test error")
    runs = db.get_runs(limit=1)
    assert runs[0]["status"] == "failed"
    assert runs[0]["error"] == "Test error"
test("PipelineRun — failed run بيتسجل صح", test_failed_run)


# ═══════════════════════════════════════════════════════
# 5. Posts CRUD
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 5: Posts CRUD")
print("═"*55)

MOCK_POSTS = [
    {"title": "AI agents replacing devs",    "source": "reddit",    "url": "http://r.com/1", "score": 150,
     "cluster": 0, "trend_score": 21.0, "trend_state": "exploding", "cluster_state": "exploding"},
    {"title": "Rust vs Go performance",      "source": "hackernews","url": "http://h.com/1", "score": 200,
     "cluster": 1, "trend_score": 14.0, "trend_state": "growing",   "cluster_state": "growing"},
    {"title": "WebAssembly in production",   "source": "devto",     "url": "http://d.com/1", "score": 70,
     "cluster": 2, "trend_score": 3.0,  "trend_state": "stable",    "cluster_state": "stable"},
    {"title": "",                            "source": "test",      "url": "", "score": 0},  # empty — يتشال
]

def test_save_and_get_posts():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()

    saved = db.save_posts(MOCK_POSTS, run_id)
    assert saved == 3, f"المفروض 3 posts (الـ empty يتشال)، لقينا {saved}"

    posts = db.get_posts(run_id=run_id)
    assert len(posts) == 3, f"المفروض 3 posts في الـ DB، لقينا {len(posts)}"
test("Posts — save_posts() يحفظ ويشيل empty titles", test_save_and_get_posts)

def test_filter_posts_by_state():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    db.save_posts(MOCK_POSTS, run_id)

    exploding = db.get_posts(run_id=run_id, trend_state="exploding")
    assert len(exploding) == 1, f"المفروض 1 exploding، لقينا {len(exploding)}"
    assert exploding[0]["title"] == "AI agents replacing devs"
test("Posts — filter بـ trend_state شغال", test_filter_posts_by_state)


# ═══════════════════════════════════════════════════════
# 6. Trends CRUD
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 6: Trends CRUD")
print("═"*55)

MOCK_RANKED = {
    "exploding": [
        {"title": "AI agents", "cluster": 0, "trend_score": 21.0,
         "trend_state": "exploding", "cluster_score": 18.0, "forecast": "viral"},
    ],
    "growing": [
        {"title": "Rust perf", "cluster": 1, "trend_score": 14.0,
         "trend_state": "growing",   "cluster_score": 12.0, "forecast": "future_trend"},
    ],
    "future":  [],
    "stable":  [
        {"title": "WebAssembly", "cluster": 2, "trend_score": 3.0,
         "trend_state": "stable",   "cluster_score": 3.0,  "forecast": "stable"},
    ],
}

def test_save_and_get_trends():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()

    saved = db.save_trends(MOCK_RANKED, run_id)
    assert saved == 3, f"المفروض 3 trends، لقينا {saved}"

    trends = db.get_trends(run_id=run_id)
    assert len(trends) == 3
test("Trends — save_trends() و get_trends() شغالين", test_save_and_get_trends)

def test_filter_trends_by_state():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    db.save_trends(MOCK_RANKED, run_id)

    exploding = db.get_trends(run_id=run_id, cluster_state="exploding")
    assert len(exploding) == 1
    assert exploding[0]["cluster_state"] == "exploding"
test("Trends — filter بـ cluster_state شغال", test_filter_trends_by_state)

def test_trends_json_fields_parsed():
    """top_topics و keywords المفروض يرجعوا كـ list مش string"""
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    db.save_trends(MOCK_RANKED, run_id)

    trends = db.get_trends(run_id=run_id)
    for t in trends:
        assert isinstance(t["top_topics"], list), "top_topics المفروض list"
        assert isinstance(t["keywords"],   list), "keywords المفروض list"
test("Trends — top_topics و keywords بيرجعوا كـ list", test_trends_json_fields_parsed)


# ═══════════════════════════════════════════════════════
# 7. Content CRUD
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 7: Content CRUD")
print("═"*55)

MOCK_CONTENT = """
## INSTAGRAM POST
Check out these AI trends dominating tech right now! 🤖 #AI #Tech

## LINKEDIN POST
AI agents are transforming how development teams operate...

## TWITTER THREAD
1/ AI agents are replacing junior devs faster than expected.
2/ Here's what you need to know...

## SHORT VIDEO SCRIPT
Hook: Did you know AI agents can now write code better than juniors?
"""

def test_save_and_get_content():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()

    content_id = db.save_content("strategy text", MOCK_CONTENT, run_id)
    assert content_id is not None and content_id > 0

    latest = db.get_latest_content()
    assert latest is not None
    assert "strategy" in latest
test("Content — save_content() و get_latest_content() شغالين", test_save_and_get_content)

def test_content_sections_extracted():
    """المفروض يقسم المحتوى لـ sections منفصلة"""
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    run_id = db.start_run()
    db.save_content("strategy", MOCK_CONTENT, run_id)

    latest = db.get_latest_content()
    assert latest["instagram"] != "", "instagram section فاضية"
    assert latest["linkedin"]  != "", "linkedin section فاضية"
    assert latest["twitter"]   != "", "twitter section فاضية"
    assert latest["video"]     != "", "video section فاضية"
test("Content — يستخرج الـ 4 sections صح", test_content_sections_extracted)


# ═══════════════════════════════════════════════════════
# 8. Stats
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 8: Stats")
print("═"*55)

def test_get_stats():
    from engine.database.db import DatabaseManager
    db = DatabaseManager(TEST_DB_PATH)
    stats = db.get_stats()
    assert "total_posts"  in stats
    assert "total_trends" in stats
    assert "total_runs"   in stats
    assert "exploding"    in stats
    assert "growing"      in stats
    assert all(isinstance(v, int) for v in stats.values())
test("DatabaseManager.get_stats() — يرجع dict بـ 5 keys كلها int", test_get_stats)


# ═══════════════════════════════════════════════════════
# 9. get_db Singleton
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
print("Sprint 3 — Task 9: Singleton")
print("═"*55)

def test_get_db_singleton():
    from engine.database.db import get_db
    db1 = get_db()
    db2 = get_db()
    assert db1 is db2, "get_db() المفروض يرجع نفس الـ instance"
test("get_db() — singleton pattern شغال", test_get_db_singleton)


# ═══════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

# ═══════════════════════════════════════════════════════
# Final Report
# ═══════════════════════════════════════════════════════
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 3 اكتمل بنجاح!")
    print("\n    الـ Database جاهز في: data/db/intelligence.db")
    print("    الـ Pipeline دلوقتي بيحفظ في DB + JSON")
else:
    print(f"⚠️   {failed} اختبار فشل — راجع الأخطاء فوق")
print("═"*55 + "\n")

sys.exit(0 if failed == 0 else 1)