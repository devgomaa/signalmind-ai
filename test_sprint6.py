"""
test_sprint6.py — Sprint 6: SaaS Platform
شغّله: python test_sprint6.py
"""
import sys, traceback, os

passed = 0
failed = 0
TEST_DB = "data/db/test_sprint6.db"

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

# ── 1. Auth Models ─────────────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 1: Auth Models")
print("═"*55)

def test_models_import():
    from engine.auth.models import User, Workspace, Competitor, NICHES, MARKETS
    assert len(NICHES) == 7
    assert len(MARKETS) == 6
    u = User(email="a@b.com", password_hash="xxx", name="Test")
    assert u.role == "admin"
    assert u.workspace_id == 1
test("Models — User, Workspace, Competitor + NICHES/MARKETS", test_models_import)

def test_workspace_markets():
    from engine.auth.models import Workspace
    ws = Workspace(name="Test WS")
    ws.set_markets(["egypt", "saudi"])
    assert ws.get_markets() == ["egypt", "saudi"]
test("Workspace.get/set_markets() JSON serialization", test_workspace_markets)

# ── 2. AuthManager ─────────────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 2: AuthManager")
print("═"*55)

def test_auth_tables():
    import sqlite3
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB; auth._create_tables()
    conn = sqlite3.connect(TEST_DB)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    for t in ["users","workspaces","competitors"]:
        assert t in tables, f"Table {t} missing"
test("AuthManager — creates users, workspaces, competitors tables", test_auth_tables)

def test_register_login():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB; auth._create_tables()
    result = auth.register("test@test.com","pass123","Test User","Test WS","tech",["egypt"])
    assert result["ok"], f"Register failed: {result}"
    assert "token" in result
    login = auth.login("test@test.com","pass123")
    assert login["ok"], f"Login failed: {login}"
    assert "token" in login
    assert login["name"] == "Test User"
test("register() + login() flow", test_register_login)

def test_wrong_password():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    result = auth.login("test@test.com","wrongpass")
    assert not result["ok"]
test("login() rejects wrong password", test_wrong_password)

def test_duplicate_email():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    result = auth.register("test@test.com","pass123","Test2","WS2","tech",["global"])
    assert not result["ok"], "Should reject duplicate email"
test("register() rejects duplicate email", test_duplicate_email)

def test_token_verify():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    login = auth.login("test@test.com","pass123")
    payload = auth.verify_token(login["token"])
    assert payload is not None
    assert payload["user_id"] == login["user_id"]
    assert payload["workspace_id"] == login["workspace_id"]
test("JWT token generation + verification", test_token_verify)

def test_invalid_token():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    assert auth.verify_token("invalid.token.here") is None
test("verify_token() rejects invalid token", test_invalid_token)

# ── 3. Workspace Management ────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 3: Workspace Management")
print("═"*55)

def test_workspace_crud():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    ws = auth.get_workspace(1)
    assert ws is not None
    assert "niche" in ws
    assert "markets" in ws
    assert isinstance(ws["markets"], list)
test("get_workspace() returns workspace with parsed markets", test_workspace_crud)

def test_workspace_update():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    auth.update_workspace(1, niche="ai_startup", markets=["egypt","saudi"])
    ws = auth.get_workspace(1)
    assert ws["niche"] == "ai_startup"
    assert "egypt" in ws["markets"]
test("update_workspace() niche + markets", test_workspace_update)

def test_competitors():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    cid = auth.add_competitor(1,"TechCrunch","https://techcrunch.com","publication")
    comps = auth.get_competitors(1)
    assert any(c["id"]==cid for c in comps)
    auth.delete_competitor(cid, 1)
    comps2 = auth.get_competitors(1)
    assert not any(c["id"]==cid for c in comps2)
test("add_competitor() + get + delete", test_competitors)

def test_team_invite():
    from engine.auth.auth_manager import AuthManager
    auth = AuthManager(); auth.db_path = TEST_DB
    result = auth.invite_user("member@test.com","Team Member","editor",1)
    assert result["ok"]
    users = auth.get_workspace_users(1)
    assert any(u["email"]=="member@test.com" for u in users)
test("invite_user() + get_workspace_users()", test_team_invite)

# ── 4. Niche Config ────────────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 4: Niche Config")
print("═"*55)

def test_niche_config():
    from engine.workspace.niche_config import NICHE_CONFIG, MARKET_CONFIG
    assert len(NICHE_CONFIG) == 7
    assert len(MARKET_CONFIG) == 6
    for niche, cfg in NICHE_CONFIG.items():
        assert "keywords"          in cfg, f"{niche}: keywords missing"
        assert "reddit_subs"       in cfg, f"{niche}: reddit_subs missing"
        assert "google_news_query" in cfg, f"{niche}: google_news_query missing"
test("NICHE_CONFIG — 7 niches with full config", test_niche_config)

def test_niche_prompt():
    from engine.workspace.niche_config import get_niche_prompt, get_deep_search_prompt
    prompt = get_niche_prompt("ai_startup", ["egypt","global"], ["AI agents","LangChain","RAG"])
    assert "AI / Startups" in prompt
    assert len(prompt) > 100
    deep = get_deep_search_prompt("tech", ["saudi"])
    assert "software" in deep.lower() or "tech" in deep.lower()
test("get_niche_prompt() + get_deep_search_prompt() generate correct prompts", test_niche_prompt)

# ── 5. Flask API ───────────────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 5: Flask API Endpoints")
print("═"*55)

def test_auth_endpoints():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        # register
        r = c.post('/api/auth/register', json={
            "email":"sprint6@test.com","password":"test123",
            "name":"Sprint6","niche":"tech","markets":["egypt"]
        })
        assert r.status_code == 200
        token = r.get_json()["data"]["token"]

        # login
        r2 = c.post('/api/auth/login', json={"email":"sprint6@test.com","password":"test123"})
        assert r2.status_code == 200

        # me
        r3 = c.get('/api/auth/me', headers={"Authorization":f"Bearer {token}"})
        assert r3.status_code == 200
        data = r3.get_json()["data"]
        assert data["user"]["name"] == "Sprint6"
test("POST /api/auth/register → login → GET /api/auth/me", test_auth_endpoints)

def test_workspace_endpoints():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.post('/api/auth/login', json={"email":"sprint6@test.com","password":"test123"})
        token = r.get_json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        ws = c.get('/api/workspace', headers=headers)
        assert ws.status_code == 200

        upd = c.put('/api/workspace', json={"niche":"marketing"}, headers=headers)
        assert upd.status_code == 200
test("GET /api/workspace + PUT update niche", test_workspace_endpoints)

def test_competitor_endpoints():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.post('/api/auth/login', json={"email":"sprint6@test.com","password":"test123"})
        token = r.get_json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        add = c.post('/api/workspace/competitors', json={"name":"Competitor X","url":"http://x.com"}, headers=headers)
        assert add.status_code == 200
        cid = add.get_json()["data"]["id"]

        get = c.get('/api/workspace/competitors', headers=headers)
        assert get.status_code == 200
        assert get.get_json()["data"]["count"] >= 1

        delete = c.delete(f'/api/workspace/competitors/{cid}', headers=headers)
        assert delete.status_code == 200
test("POST/GET/DELETE /api/workspace/competitors", test_competitor_endpoints)

def test_team_endpoints():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.post('/api/auth/login', json={"email":"sprint6@test.com","password":"test123"})
        token = r.get_json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        team = c.get('/api/workspace/team', headers=headers)
        assert team.status_code == 200
        assert team.get_json()["data"]["count"] >= 1
test("GET /api/workspace/team", test_team_endpoints)

def test_protected_route():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/api/workspace')
        assert r.status_code == 401, "Should return 401 without token"
test("Protected route returns 401 without token", test_protected_route)

# ── 6. Login Page ──────────────────────────────
print("\n" + "═"*55)
print("Sprint 6 — Task 6: Login Page")
print("═"*55)

def test_login_page():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        r = c.get('/login')
        assert r.status_code == 200
        assert b'TrendPulse' in r.data
        assert b'Sign In' in r.data
        assert b'niche' in r.data.lower()
test("GET /login returns login page with niche selection", test_login_page)

def test_niches_markets_endpoints():
    from api.app import create_app
    app = create_app()
    with app.test_client() as c:
        niches  = c.get('/api/auth/niches').get_json()["data"]
        markets = c.get('/api/auth/markets').get_json()["data"]
        assert len(niches)  == 7
        assert len(markets) == 6
test("GET /api/auth/niches (7) + /api/auth/markets (6)", test_niches_markets_endpoints)

# ── Cleanup ────────────────────────────────────
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# ── Final ──────────────────────────────────────
print("\n" + "═"*55)
total = passed + failed
print(f"النتيجة: {passed}/{total} اختبارات نجحت")
if failed == 0:
    print("🎉  Sprint 6 اكتمل بنجاح!")
    print("\n    الجديد:")
    print("    ✦ User auth (JWT + bcrypt)")
    print("    ✦ Workspaces + Teams + Roles")
    print("    ✦ 7 Niches × 6 Markets")
    print("    ✦ Competitor tracking")
    print("    ✦ APScheduler per workspace")
    print("    ✦ Topic Graph visualization")
    print("    ✦ Login page + protected routes")
else:
    print(f"⚠️   {failed} فشلوا")
print("═"*55+"\n")
sys.exit(0 if failed == 0 else 1)
