"""
test_sprint5.py
===============
اختبار Sprint 5: API + Dashboard
شغّله: python test_sprint5.py
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
        traceback.print_exc()
        failed += 1

# ── App Factory ───────────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 1: Flask App")
print("═"*55)

def test_app_creates():
    from api.app import create_app
    app = create_app()
    assert app is not None
    assert app.template_folder is not None
test("Flask app — create_app() شغال", test_app_creates)

def test_health_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data['status'] == 'ok'
test("GET /health — يرجع 200", test_health_endpoint)

def test_dashboard_route():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/')
        assert r.status_code == 200
        assert b'TrendPulse' in r.data
test("GET / — يرجع dashboard.html", test_dashboard_route)

# ── Trends Endpoints ──────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 2: Trend Endpoints")
print("═"*55)

def test_trends_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/trends')
        assert r.status_code == 200
        d = r.get_json()
        assert d['status'] == 'ok'
        assert 'trends' in d['data']
test("GET /api/trends — يرجع 200 + trends list", test_trends_endpoint)

def test_trends_stats():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/trends/stats')
        assert r.status_code == 200
        d = r.get_json()['data']
        for key in ['total_posts','total_trends','exploding','growing','total_runs']:
            assert key in d, f"{key} مش موجود"
test("GET /api/trends/stats — يرجع كل الـ KPIs", test_trends_stats)

def test_trends_filter():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        for state in ['exploding','growing','future','stable']:
            r = c.get(f'/api/trends?state={state}')
            assert r.status_code == 200
test("GET /api/trends?state=X — filter شغال", test_trends_filter)

def test_exploding_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/trends/exploding')
        assert r.status_code == 200
test("GET /api/trends/exploding — يرجع 200", test_exploding_endpoint)

def test_sources_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/trends/sources')
        assert r.status_code == 200
        d = r.get_json()['data']
        assert 'sources' in d
test("GET /api/trends/sources — يرجع source distribution", test_sources_endpoint)

# ── Content Endpoints ─────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 3: Content Endpoints")
print("═"*55)

def test_content_latest():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/content/latest')
        # 200 لو في content، 404 لو مفيش — كلاهما مقبول
        assert r.status_code in [200, 404]
        d = r.get_json()
        assert d['status'] in ['ok', 'error']
test("GET /api/content/latest — يرجع 200 أو 404", test_content_latest)

# ── Pipeline Endpoints ────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 4: Pipeline Endpoints")
print("═"*55)

def test_pipeline_status():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/pipeline/status')
        assert r.status_code == 200
        d = r.get_json()['data']
        assert 'is_running' in d
test("GET /api/pipeline/status — يرجع status", test_pipeline_status)

def test_pipeline_run_post():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.post('/api/pipeline/run')
        # 200 أو 409 (already running) — كلاهما صح
        assert r.status_code in [200, 409]
test("POST /api/pipeline/run — يقبل request", test_pipeline_run_post)

# ── Scraping Endpoints ────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 5: Scraping Endpoints")
print("═"*55)

def test_posts_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/posts')
        assert r.status_code == 200
        d = r.get_json()['data']
        assert 'posts' in d
test("GET /api/posts — يرجع posts list", test_posts_endpoint)

def test_runs_endpoint():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/runs')
        assert r.status_code == 200
        d = r.get_json()['data']
        assert 'runs' in d
test("GET /api/runs — يرجع runs list", test_runs_endpoint)

# ── Dashboard HTML ────────────────────────────────
print("\n" + "═"*55)
print("Sprint 5 — Task 6: Dashboard")
print("═"*55)

def test_dashboard_has_charts():
    import os
    path = os.path.join("dashboard","templates","dashboard.html")
    assert os.path.exists(path), "dashboard.html مش موجود"
    with open(path) as f:
        html = f.read()
    assert 'Chart.js' in html or 'chart.umd' in html, "Chart.js مش موجود"
    assert 'TrendPulse' in html, "Brand name مش موجود"
    assert 'velocity-chart' in html, "velocity chart مش موجود"
    assert 'sources-chart' in html,  "sources chart مش موجود"
test("dashboard.html — Chart.js + كل الـ charts موجودين", test_dashboard_has_charts)

def test_dashboard_has_api_calls():
    import os
    with open(os.path.join("dashboard","templates","dashboard.html")) as f:
        html = f.read()
    for endpoint in ['/api/trends/stats', '/api/trends/latest',
                     '/api/trends/sources', '/api/pipeline/run']:
        assert endpoint in html, f"API call {endpoint} مش موجود في dashboard"
test("dashboard.html — كل الـ API endpoints متربطة", test_dashboard_has_api_calls)

def test_dashboard_interactive():
    import os
    with open(os.path.join("dashboard","templates","dashboard.html")) as f:
        html = f.read()
    assert 'triggerPipeline' in html, "triggerPipeline مش موجود"
    assert 'filterTrends'    in html, "filterTrends مش موجود"
    assert 'showPage'        in html, "navigation مش موجود"
    assert 'pollStatus'      in html, "pollStatus مش موجود"
test("dashboard.html — interactive functions موجودة", test_dashboard_interactive)

# ── Final ─────────────────────────────────────────
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 5 اكتمل بنجاح!")
    print("\n    لتشغيل الـ Dashboard:")
    print("    python -m flask --app api/app.py run --port 5000")
    print("    ثم افتح: http://localhost:5000")
else:
    print(f"⚠️   {failed} فشلوا")
print("═"*55 + "\n")
sys.exit(0 if failed == 0 else 1)
