"""
test_sprint7.py — Sprint 7
شغّله: python test_sprint7.py
"""
import sys, traceback, os

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

# ── 1. Niche Config ────────────────────────────
print("\n" + "═"*55)
print("Sprint 7 — Task 1: Niche Config (25+ niches + MENA)")
print("═"*55)

def test_niches_count():
    from engine.workspace.niche_config import NICHE_CONFIG, NICHES
    assert len(NICHES) >= 25, f"المفروض 25+ niche، لقينا {len(NICHES)}"
test("NICHE_CONFIG — 25+ niches", test_niches_count)

def test_markets_count():
    from engine.workspace.niche_config import MARKET_CONFIG, MARKETS
    assert len(MARKETS) >= 20, f"المفروض 20+ market، لقينا {len(MARKETS)}"
    # تحقق من دول المنطقة
    for country in ["egypt","saudi","uae","kuwait","qatar","bahrain","oman","jordan","morocco","algeria","tunisia"]:
        assert country in MARKET_CONFIG, f"{country} مش موجود"
test("MARKET_CONFIG — 20+ MENA countries", test_markets_count)

def test_platforms_config():
    from engine.workspace.niche_config import PLATFORM_CONFIG, PLATFORMS
    assert len(PLATFORMS) == 14, f"المفروض 14 platforms، لقينا {len(PLATFORMS)}"
test("PLATFORM_CONFIG — 14 platforms", test_platforms_config)

def test_niche_has_required_fields():
    from engine.workspace.niche_config import NICHE_CONFIG
    required = ["label","emoji","keywords","reddit_subs","google_news_query"]
    for niche, cfg in NICHE_CONFIG.items():
        for field in required:
            assert field in cfg, f"{niche}: {field} missing"
test("كل niche له label + emoji + keywords + config", test_niche_has_required_fields)

def test_competitor_prompt():
    from engine.workspace.niche_config import get_competitor_suggestions_prompt
    prompt = get_competitor_suggestions_prompt("marketing", ["egypt","global"])
    assert "JSON" in prompt or "json" in prompt.lower()
    assert len(prompt) > 50
test("get_competitor_suggestions_prompt() يولّد JSON prompt", test_competitor_prompt)

# ── 2. Content Studio ──────────────────────────
print("\n" + "═"*55)
print("Sprint 7 — Task 2: Content Studio")
print("═"*55)

def test_studio_imports():
    from engine.content.content_studio import (
        ContentStudio, PollinationsGenerator,
        HTMLCardGenerator, VideoSlideshowGenerator,
        GeneratedPost, GeneratedVideo
    )
test("ContentStudio — all classes importable", test_studio_imports)

def test_pollinations_url():
    from engine.content.content_studio import PollinationsGenerator, POLLINATIONS
    assert "pollinations.ai" in POLLINATIONS
test("PollinationsGenerator — URL صح", test_pollinations_url)

def test_html_card_generates():
    from engine.content.content_studio import HTMLCardGenerator
    idea = {
        "hook": "Test hook for social media",
        "post_copy": "This is a test post copy for testing purposes.",
        "hashtags": ["test", "AI", "trends"],
        "image_description": "A futuristic tech scene",
    }
    path = HTMLCardGenerator.generate(idea, ["#3B82F6"], "test_card.png")
    assert path is not None
    # HTML or PNG should exist
    html_path = path.replace(".png", ".html")
    assert os.path.exists(path) or os.path.exists(html_path)
test("HTMLCardGenerator — يولّد HTML card fallback", test_html_card_generates)

def test_static_schema():
    from engine.content.content_studio import ContentStudio
    studio = ContentStudio()
    schema = studio._static_schema(3, "English")
    assert "ideas" in schema
    assert "hook" in schema
    assert "image_description" in schema
test("ContentStudio._static_schema() — schema صح", test_static_schema)

def test_video_schema():
    from engine.content.content_studio import ContentStudio
    studio = ContentStudio()
    schema = studio._video_schema(2, "Arabic")
    assert "script" in schema
    assert "visuals" in schema
    assert "voiceover" in schema
test("ContentStudio._video_schema() — schema صح", test_video_schema)

# ── 3. Plan Exporter ───────────────────────────
print("\n" + "═"*55)
print("Sprint 7 — Task 3: Plan Exporter (PDF + Excel)")
print("═"*55)

MOCK_TRENDS = {
    "exploding": [{"cluster_id":1,"cluster_state":"exploding","cluster_score":22.0,"top_topics":["AI agents"],"forecast":"viral"}],
    "growing":   [{"cluster_id":2,"cluster_state":"growing",  "cluster_score":14.0,"top_topics":["LangChain"],"forecast":"future_trend"}],
    "future":    [],
    "stable":    [{"cluster_id":3,"cluster_state":"stable",   "cluster_score":3.0, "top_topics":["WebAssembly"],"forecast":"stable"}],
}
MOCK_STRATEGY = "## Content Strategy\n1. Create AI posts\n2. Target LinkedIn\n## Video Ideas\n- Short clips"
MOCK_IDEAS    = [{"idea_index":1,"hook":"AI is changing everything","post_copy":"Full copy here","hashtags":["AI","tech"],"status":"completed"}]

def test_exporter_import():
    from engine.content.plan_exporter import PlanExporter
    exp = PlanExporter()
    assert hasattr(exp, "export_pdf")
    assert hasattr(exp, "export_excel")
test("PlanExporter — import صح", test_exporter_import)

def test_pdf_export():
    from engine.content.plan_exporter import PlanExporter
    exp  = PlanExporter()
    path = exp.export_pdf("Test Workspace", "ai_startup", MOCK_STRATEGY, MOCK_TRENDS, MOCK_IDEAS)
    assert os.path.exists(path), f"PDF not found: {path}"
    assert os.path.getsize(path) > 100
    print(f"\n       PDF saved: {path}")
test("PlanExporter.export_pdf() — ينولّد PDF حقيقي", test_pdf_export)

def test_excel_export():
    from engine.content.plan_exporter import PlanExporter
    exp  = PlanExporter()
    path = exp.export_excel("Test Workspace", "ai_startup", MOCK_STRATEGY, MOCK_TRENDS, MOCK_IDEAS)
    assert os.path.exists(path), f"Excel not found: {path}"
    assert os.path.getsize(path) > 100
    print(f"\n       Excel saved: {path}")
test("PlanExporter.export_excel() — يولّد Excel/CSV حقيقي", test_excel_export)

# ── 4. API Endpoints ───────────────────────────
print("\n" + "═"*55)
print("Sprint 7 — Task 4: API Endpoints")
print("═"*55)

def test_studio_blueprint():
    from api.app import create_app
    app = create_app()
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert any('/api/studio/generate' in r for r in rules), "studio/generate endpoint missing"
    assert any('/api/studio/export/pdf' in r for r in rules), "export/pdf endpoint missing"
    assert any('/api/studio/export/excel' in r for r in rules), "export/excel endpoint missing"
    assert any('/api/content/media' in r for r in rules), "media endpoint missing"
test("Flask — studio endpoints registered", test_studio_blueprint)

def test_discover_competitors_endpoint():
    from api.app import create_app
    app = create_app()
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert any('competitors/discover' in r for r in rules), "competitors/discover endpoint missing"
test("Flask — /api/workspace/competitors/discover registered", test_discover_competitors_endpoint)

def test_generate_requires_auth():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.post('/api/studio/generate', json={"topic":"test"})
        assert r.status_code == 401
test("POST /api/studio/generate — requires auth (401)", test_generate_requires_auth)

def test_generate_with_auth():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        # Register + login
        c.post('/api/auth/register', json={
            "email":"studio7@test.com","password":"test123",
            "name":"Studio7","niche":"ai_startup","markets":["egypt"]
        })
        r = c.post('/api/auth/login', json={"email":"studio7@test.com","password":"test123"})
        token = r.get_json()["data"]["token"]

        # Generate (background job)
        gen = c.post('/api/studio/generate',
            json={"topic":"AI trends","content_type":"static","num_ideas":1},
            headers={"Authorization":f"Bearer {token}"}
        )
        assert gen.status_code == 200
        data = gen.get_json()["data"]
        assert "job_id" in data
test("POST /api/studio/generate with auth → returns job_id", test_generate_with_auth)

# ── 5. Niche Config API ───────────────────────
print("\n" + "═"*55)
print("Sprint 7 — Task 5: Updated Niche/Market APIs")
print("═"*55)

def test_niches_api_returns_25():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/auth/niches')
        niches = r.get_json()["data"]
        assert len(niches) >= 25, f"المفروض 25+، لقينا {len(niches)}"
test("GET /api/auth/niches — يرجع 25+ niches", test_niches_api_returns_25)

def test_markets_api_returns_20():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/auth/markets')
        markets = r.get_json()["data"]
        assert len(markets) >= 20, f"المفروض 20+، لقينا {len(markets)}"
test("GET /api/auth/markets — يرجع 20+ markets", test_markets_api_returns_20)

# ── Cleanup ────────────────────────────────────
import shutil
for d in ["output_content", "output_exports"]:
    if os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)

# ── Final ──────────────────────────────────────
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 7 اكتمل بنجاح!")
    print("\n    الجديد:")
    print("    ✦ 25+ Niches + 20+ MENA countries")
    print("    ✦ Content Studio (Pollinations + HTML fallback)")
    print("    ✦ Video Slideshow (moviepy + Pollinations)")
    print("    ✦ PDF + Excel export")
    print("    ✦ Auto Competitor Discovery")
    print("    ✦ D3.js Force Graph")
    print("    ✦ Platform Selector")
else:
    print(f"⚠️   {failed} فشلوا")
print("═"*55+"\n")
sys.exit(0 if failed == 0 else 1)
