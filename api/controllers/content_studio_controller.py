"""api/controllers/content_studio_controller.py — Sprint 7 (media service ready)"""

import os
import threading
from flask import Blueprint, jsonify, request, g, send_file, current_app

from engine.auth.decorators import require_auth
from engine.database import get_db
from engine.utils.logger import get_logger

studio_bp = Blueprint("studio", __name__)
logger = get_logger("ContentStudioController")

_active_jobs = {}   # job_id → {"status", "result", "error"}


def _ok(d):
    return jsonify({"status": "ok", "data": d})


def _err(m, c=400):
    return jsonify({"status": "error", "message": m}), c


# ─────────────────────────────────────────────
# Generate Content
# ─────────────────────────────────────────────

@studio_bp.route("/studio/generate", methods=["POST"])
@require_auth
def generate():

    data = request.get_json() or {}

    topic        = data.get("topic", "").strip()
    content_type = data.get("content_type", "static")
    num_ideas    = int(data.get("num_ideas", 3))
    platforms    = data.get("platforms", ["Instagram", "LinkedIn"])
    brand_colors = data.get("brand_colors", ["#3B82F6"])
    language     = data.get("language", "English")

    if not topic:
        return _err("topic required")

    if content_type not in ("static", "video"):
        return _err("content_type must be 'static' or 'video'")

    # ── Workspace Info ──
    from engine.auth.auth_manager import get_auth

    ws    = get_auth().get_workspace(g.workspace_id)
    niche = ws.get("niche", "tech") if ws else "tech"

    # ── Trend Insight ──
    db = get_db()
    trends = db.get_latest_trends()

    trend_insight = None
    if trends:
        top_topics = [t.get("top_topics", []) for t in trends[:5]]
        trend_insight = ", ".join(t[0] for t in top_topics if t)

    workspace_id = g.workspace_id

    # ── Create Job ──
    import uuid
    job_id = str(uuid.uuid4())[:8]

    _active_jobs[job_id] = {
        "status": "running",
        "result": None,
        "error": None
    }

    app = current_app._get_current_object()

    # ─────────────────────────────────────────
    # Background Worker
    # ─────────────────────────────────────────

    def run_job():

        with app.app_context():

            try:

                from engine.content.content_studio import ContentStudio

                studio = ContentStudio(workspace_id=workspace_id)

                result = studio.generate_content(
                    topic         = topic,
                    content_type  = content_type,
                    niche         = niche,
                    language      = language,
                    brand_colors  = brand_colors,
                    num_ideas     = num_ideas,
                    platforms     = platforms,
                    trend_insight = trend_insight,
                )

                _active_jobs[job_id]["result"] = result
                _active_jobs[job_id]["status"] = "completed"

            except Exception as e:

                _active_jobs[job_id]["error"]  = str(e)
                _active_jobs[job_id]["status"] = "failed"

                logger.error(f"Studio job {job_id} failed: {e}")

    t = threading.Thread(target=run_job, daemon=True)
    t.start()

    return _ok({
        "job_id": job_id,
        "message": "Generation started"
    })


# ─────────────────────────────────────────────
# Job Status
# ─────────────────────────────────────────────

@studio_bp.route("/studio/jobs/<job_id>")
@require_auth
def job_status(job_id):

    job = _active_jobs.get(job_id)

    if not job:
        return _err("Job not found", 404)

    return _ok(job)


# ─────────────────────────────────────────────
# Media Serving
# ─────────────────────────────────────────────

@studio_bp.route("/content/media/<filename>")
def serve_media(filename):
    """
    Serve generated media files (images / videos).
    Supports both output_content and new media folders.
    """

    possible_paths = [
        os.path.join("output_content", filename),
        os.path.join("output_posts", filename),
        os.path.join("output_videos", filename),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return send_file(path)

    return _err("File not found", 404)


# ─────────────────────────────────────────────
# Export PDF
# ─────────────────────────────────────────────

@studio_bp.route("/studio/export/pdf", methods=["POST"])
@require_auth
def export_pdf():

    data  = request.get_json() or {}
    ideas = data.get("ideas", [])

    from engine.auth.auth_manager import get_auth

    ws      = get_auth().get_workspace(g.workspace_id)
    ws_name = ws.get("name", "My Workspace") if ws else "Workspace"
    niche   = ws.get("niche", "tech") if ws else "tech"

    db = get_db()

    trends = db.get_latest_trends()

    strategy_data = db.get_latest_content()
    strategy = strategy_data.get("strategy", "") if strategy_data else ""

    trends_dict = {
        "exploding": [],
        "growing": [],
        "future": [],
        "stable": []
    }

    for t in trends:
        state = t.get("cluster_state", "stable")
        if state in trends_dict:
            trends_dict[state].append(t)

    from engine.content.plan_exporter import PlanExporter

    path = PlanExporter().export_pdf(
        ws_name,
        niche,
        strategy,
        trends_dict,
        ideas
    )

    return send_file(
        path,
        as_attachment=True,
        download_name=os.path.basename(path),
    )


# ─────────────────────────────────────────────
# Export Excel
# ─────────────────────────────────────────────

@studio_bp.route("/studio/export/excel", methods=["POST"])
@require_auth
def export_excel():

    data  = request.get_json() or {}
    ideas = data.get("ideas", [])

    from engine.auth.auth_manager import get_auth

    ws      = get_auth().get_workspace(g.workspace_id)
    ws_name = ws.get("name", "My Workspace") if ws else "Workspace"
    niche   = ws.get("niche", "tech") if ws else "tech"

    db = get_db()

    trends        = db.get_latest_trends()
    strategy_data = db.get_latest_content()
    strategy      = strategy_data.get("strategy", "") if strategy_data else ""
    runs          = db.get_runs(limit=20)

    trends_dict = {
        "exploding": [],
        "growing": [],
        "future": [],
        "stable": []
    }

    for t in trends:
        state = t.get("cluster_state", "stable")
        if state in trends_dict:
            trends_dict[state].append(t)

    from engine.content.plan_exporter import PlanExporter

    path = PlanExporter().export_excel(
        ws_name,
        niche,
        strategy,
        trends_dict,
        ideas,
        runs
    )

    return send_file(
        path,
        as_attachment=True,
        download_name=os.path.basename(path),
    )


# ─────────────────────────────────────────────
# Auto Competitor Discovery
# ─────────────────────────────────────────────

@studio_bp.route("/workspace/competitors/discover", methods=["POST"])
@require_auth
def discover_competitors():

    import json
    import re

    from engine.auth.auth_manager import get_auth
    from engine.workspace.niche_config import get_competitor_suggestions_prompt
    from engine.ai.gemini_client import GeminiClient

    ws      = get_auth().get_workspace(g.workspace_id)
    niche   = ws.get("niche", "tech") if ws else "tech"
    markets = ws.get("markets", ["global"]) if ws else ["global"]

    prompt = get_competitor_suggestions_prompt(niche, markets)

    try:

        llm = GeminiClient()

        raw = llm.ask(prompt, max_tokens=1000)

        match = re.search(r'\[[\s\S]*\]', raw)

        if not match:
            return _err("Could not parse competitor suggestions")

        suggestions = json.loads(match.group())

        return _ok({
            "suggestions": suggestions[:10]
        })

    except Exception as e:

        return _err(f"Discovery failed: {e}")