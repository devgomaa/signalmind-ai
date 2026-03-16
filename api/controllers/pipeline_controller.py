"""api/controllers/pipeline_controller.py — Sprint 7 (updated)

التغيير: الـ /api/pipeline/run بقى يقبل config:
    {
        "niche":     "education",
        "markets":   ["egypt", "saudi"],
        "platforms": ["reddit", "youtube", "hackernews"],
        "keywords":  ["optional custom keywords"]  ← اختياري
    }

لو مفيش config → يستخدم إعدادات الـ workspace تلقائياً.
"""

import threading
from flask import Blueprint, jsonify, request, current_app
from engine.database import get_db
from engine.utils.logger import get_logger

pipeline_bp = Blueprint("pipeline", __name__)
logger      = get_logger("PipelineController")

_running    = False
_run_config = {}   # config آخر run


def _ok(d):         return jsonify({"status": "ok",    "data": d})
def _err(m, c=400): return jsonify({"status": "error", "message": m}), c


# ── Background runner ─────────────────────────────────────

def _run_pipeline_bg(config: dict, app):
    global _running
    with app.app_context():
        try:
            niche     = config.get("niche")
            markets   = config.get("markets")
            platforms = config.get("platforms")
            keywords  = config.get("keywords", [])

            if niche or platforms:
                # Workspace-aware pipeline مع config مخصص
                _run_with_config(niche, markets, platforms, keywords)
            else:
                # Default full pipeline
                from engine.pipelines.full_pipeline import FullPipeline
                FullPipeline().run()

        except Exception as e:
            logger.error(f"Background pipeline failed: {e}")
        finally:
            _running = False


def _run_with_config(niche, markets, platforms, keywords):
    """
    Pipeline مع إعدادات مخصصة للـ niche والـ platforms.
    """
    import time
    from engine.config import Config
    from engine.utils.data_writer import save_json
    from engine.database import get_db
    from engine.workspace.niche_config import NICHE_CONFIG, PLATFORM_CONFIG
    from engine.workspace.niche_config import get_niche_prompt, get_deep_search_prompt

    db     = get_db()
    run_id = db.start_run()
    start  = time.time()

    logger.info(f"Pipeline started — niche:{niche} platforms:{platforms}")

    try:
        # ── Step 1: Scraping (filtered by platforms) ──────────
        posts = _scrape_selected_platforms(platforms)
        logger.info(f"Collected {len(posts)} posts from {len(platforms or [])} platforms")

        # ── Step 2: Filter by niche keywords ──────────────────
        if niche and niche in NICHE_CONFIG:
            niche_kws = NICHE_CONFIG[niche]["keywords"] + keywords
            posts = _filter_by_keywords(posts, niche_kws)
            logger.info(f"After niche filter: {len(posts)} posts")

        if not posts:
            logger.warning("No posts after filtering — using unfiltered")

        save_json(Config.DATA_RAW_PATH, posts)
        db.save_posts(posts, str(run_id))

        # ── Step 3: Deep Search ────────────────────────────────
        from engine.ai.gemini_client import GeminiClient
        llm = GeminiClient()

        try:
            deep_prompt = get_deep_search_prompt(
                niche   or "tech",
                markets or ["global"]
            )
            response   = llm.ask(deep_prompt)
            deep_posts = _parse_deep_response(response)
            posts.extend(deep_posts)
            logger.info(f"Deep search added {len(deep_posts)} topics")
        except Exception as e:
            logger.warning(f"Deep search skipped: {e}")

        # ── Step 4: Trend Intelligence ─────────────────────────
        from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
        trends = TrendIntelligenceAgent().detect_trends(posts)
        save_json(Config.DATA_TRENDS_PATH, trends)
        db.save_trends(trends, str(run_id))

        # ── Step 5: Content Strategy ───────────────────────────
        flat = []
        for bucket in ["exploding", "growing", "future", "stable"]:
            flat.extend(trends.get(bucket, []))
        topics = [t.get("title", "") or
                  (t.get("top_topics", [""])[0] if t.get("top_topics") else "")
                  for t in flat[:10] if t]

        strategy = ""
        content  = ""
        try:
            strategy_prompt = get_niche_prompt(
                niche   or "tech",
                markets or ["global"],
                [t for t in topics if t]
            )
            strategy = llm.ask(strategy_prompt)
            content_prompt = f"""
Using this content strategy:
{strategy}

Generate ready-to-publish content:
## INSTAGRAM POST
## LINKEDIN POST
## TWITTER THREAD
## SHORT VIDEO SCRIPT
"""
            content = llm.ask(content_prompt)
        except Exception as e:
            logger.warning(f"Content generation skipped: {e}")

        save_json(Config.DATA_CONTENT_PATH, {"strategy": strategy, "content": content})
        if strategy:
            db.save_content(strategy, content, str(run_id))

        duration    = time.time() - start
        trend_count = sum(len(v) for v in trends.values())
        db.finish_run(run_id, len(posts), trend_count, duration)

        logger.info(f"Pipeline done in {duration:.1f}s — "
                    f"{len(posts)} posts, {trend_count} trends")

    except Exception as e:
        duration = time.time() - start
        db.finish_run(run_id, 0, 0, duration, error=str(e))
        logger.error(f"Pipeline failed: {e}")
        raise


def _scrape_selected_platforms(platforms: list) -> list:
    """يشغّل فقط الـ scrapers المختارة."""

    SCRAPER_MAP = {
        "reddit":        ("engine.scraping_sources.reddit_scraper",         "scrape_reddit"),
        "hackernews":    ("engine.scraping_sources.hackernews_scraper",      "scrape_hackernews"),
        "devto":         ("engine.scraping_sources.devto_scraper",           "scrape_devto"),
        "medium":        ("engine.scraping_sources.medium_scraper",          "scrape_medium"),
        "github":        ("engine.scraping_sources.github_trending_scraper", "scrape_github_trending"),
        "stackoverflow": ("engine.scraping_sources.stackoverflow_scraper",   "scrape_stackoverflow"),
        "youtube":       ("engine.scraping_sources.youtube_scraper",         "scrape_youtube"),
        "producthunt":   ("engine.scraping_sources.producthunt_scraper",     "scrape_producthunt"),
        "google_news":   ("engine.scraping_sources.google_news_scraper",     "scrape_google_news"),
        "google_trends": ("engine.scraping_sources.google_trends_scraper",   "scrape_google_trends"),
        "twitter":       ("engine.scraping_sources.twitter_scraper",         "scrape_twitter"),
        "linkedin":      ("engine.scraping_sources.linkedin_scraper",        "scrape_linkedin"),
        "tiktok":        ("engine.scraping_sources.tiktok_scraper",          "scrape_tiktok"),
        "instagram":     ("engine.scraping_sources.instagram_scraper",       "scrape_instagram"),
    }

    # لو مفيش selection → شغّل الكل
    to_run = platforms if platforms else list(SCRAPER_MAP.keys())

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import importlib

    posts   = []
    futures = {}

    with ThreadPoolExecutor(max_workers=len(to_run)) as executor:
        for key in to_run:
            if key not in SCRAPER_MAP:
                continue
            mod_path, fn_name = SCRAPER_MAP[key]
            try:
                mod = importlib.import_module(mod_path)
                fn  = getattr(mod, fn_name)
                futures[executor.submit(fn, 100)] = key
            except Exception as e:
                logger.error(f"Failed to load scraper {key}: {e}")

        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result(timeout=30)
                posts.extend(result)
                logger.info(f"{key} → {len(result)} posts")
            except Exception as e:
                logger.error(f"{key} scraper failed: {e}")

    return posts


def _filter_by_keywords(posts: list, keywords: list) -> list:
    """فلترة البوستات بناءً على keywords."""
    if not keywords:
        return posts
    kws      = [k.lower() for k in keywords]
    filtered = [p for p in posts if any(kw in p.get("title","").lower() for kw in kws)]
    # لو الفلترة شالت أكتر من 70% → رجّع الكل
    if len(filtered) < len(posts) * 0.3:
        logger.warning("Keyword filter too aggressive — using all posts")
        return posts
    return filtered


def _parse_deep_response(response: str) -> list:
    posts = []
    for line in response.split("\n"):
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if line[0].isdigit() and ("." in line[:3] or ")" in line[:3]):
            parts = line.split(".", 1) if "." in line[:3] else line.split(")", 1)
            if len(parts) == 2:
                line = parts[1].strip()
        elif line.startswith("-"):
            line = line[1:].strip()
        if len(line) >= 5:
            posts.append({"title": line, "url": "", "source": "deep_search", "score": 1})
    return posts


# ── API Endpoints ─────────────────────────────────────────

@pipeline_bp.route("/pipeline/run", methods=["POST"])
def trigger_run():
    global _running, _run_config

    if _running:
        return _err("Pipeline already running — please wait", 409)

    data      = request.get_json() or {}
    niche     = data.get("niche")
    markets   = data.get("markets")
    platforms = data.get("platforms")
    keywords  = data.get("keywords", [])

    # لو مفيش config → حاول تجيب من الـ workspace (لو في auth)
    if not niche and not platforms:
        try:
            from flask import g
            from engine.auth.decorators import _get_token
            from engine.auth.auth_manager import get_auth
            token = _get_token()
            if token:
                payload = get_auth().verify_token(token)
                if payload:
                    ws       = get_auth().get_workspace(payload["workspace_id"])
                    niche    = ws.get("niche")   if ws else None
                    markets  = ws.get("markets") if ws else None
        except Exception:
            pass

    config = {
        "niche":     niche,
        "markets":   markets,
        "platforms": platforms,
        "keywords":  keywords,
    }
    _run_config = config

    _running  = True
    app       = current_app._get_current_object()
    t         = threading.Thread(target=_run_pipeline_bg, args=(config, app), daemon=True)
    t.start()

    logger.info(f"Pipeline triggered — config: {config}")
    return _ok({
        "message":   "Pipeline started",
        "config":    config,
    })


@pipeline_bp.route("/pipeline/status")
def get_status():
    db     = get_db()
    runs   = db.get_runs(limit=1)
    latest = runs[0] if runs else None
    return _ok({
        "is_running":  _running,
        "latest_run":  latest,
        "run_config":  _run_config,
    })


@pipeline_bp.route("/pipeline/config-options")
def get_config_options():
    """يرجع كل الـ options المتاحة للـ Run Config dialog."""
    from engine.workspace.niche_config import (
        NICHE_CONFIG, MARKET_CONFIG, PLATFORM_CONFIG
    )
    return _ok({
        "niches": [
            {"value": k, "label": v["label"], "emoji": v["emoji"],
             "keywords": v["keywords"][:5]}
            for k, v in NICHE_CONFIG.items()
        ],
        "markets": [
            {"value": k, "label": v["label"]}
            for k, v in MARKET_CONFIG.items()
        ],
        "platforms": [
            {"value": k, "label": v["label"], "emoji": v["emoji"], "type": v["type"]}
            for k, v in PLATFORM_CONFIG.items()
        ],
    })