"""api/controllers/trend_controller.py — Sprint 5"""

from flask import Blueprint, jsonify, request
from engine.database import get_db

trends_bp = Blueprint("trends", __name__)


def _ok(data):
    return jsonify({"status": "ok", "data": data})

def _err(msg, code=400):
    return jsonify({"status": "error", "message": msg}), code


@trends_bp.route("/trends")
def get_all_trends():
    """كل الترندات — مع optional filter بـ state"""
    state = request.args.get("state")          # exploding | growing | future | stable
    limit = int(request.args.get("limit", 50))
    run_id = request.args.get("run_id")
    db = get_db()
    trends = db.get_trends(cluster_state=state, run_id=run_id, limit=limit)
    return _ok({"trends": trends, "count": len(trends)})


@trends_bp.route("/trends/latest")
def get_latest_trends():
    """ترندات آخر run ناجح"""
    state = request.args.get("state")
    db = get_db()
    trends = db.get_latest_trends(state=state)
    return _ok({"trends": trends, "count": len(trends)})


@trends_bp.route("/trends/exploding")
def get_exploding():
    db = get_db()
    return _ok({"trends": db.get_latest_trends(state="exploding")})


@trends_bp.route("/trends/growing")
def get_growing():
    db = get_db()
    return _ok({"trends": db.get_latest_trends(state="growing")})


@trends_bp.route("/trends/stats")
def get_trend_stats():
    """إحصائيات للـ Dashboard cards"""
    db = get_db()
    stats = db.get_stats()
    runs  = db.get_runs(limit=10)

    # حساب trend velocity عبر الـ runs
    history = []
    for run in reversed(runs):
        if run["status"] == "completed":
            history.append({
                "run_id":       run["id"],
                "created_at":   run["created_at"],
                "posts_count":  run["posts_count"],
                "trends_count": run["trends_count"],
                "duration_sec": run["duration_sec"],
            })

    return _ok({**stats, "run_history": history})


@trends_bp.route("/trends/sources")
def get_source_distribution():
    """توزيع البوستات على المصادر — للـ pie chart"""
    db   = get_db()
    runs = db.get_runs(limit=1)
    if not runs:
        return _ok({"sources": []})

    run_id = str(runs[0]["id"])
    posts  = db.get_posts(run_id=run_id, limit=2000)

    from collections import Counter
    counts = Counter(p["source"].split("/")[0] for p in posts)
    sources = [{"source": s, "count": c}
               for s, c in counts.most_common(14)]
    return _ok({"sources": sources})
