"""api/controllers/scraping_controller.py — Sprint 5"""
from flask import Blueprint, jsonify, request
from engine.database import get_db

scraping_bp = Blueprint("scraping", __name__)

def _ok(d):     return jsonify({"status": "ok",    "data": d})
def _err(m, c=400): return jsonify({"status": "error", "message": m}), c


@scraping_bp.route("/posts")
def get_posts():
    state  = request.args.get("state")
    run_id = request.args.get("run_id")
    limit  = int(request.args.get("limit", 100))
    db = get_db()
    posts = db.get_posts(run_id=run_id, trend_state=state, limit=limit)
    return _ok({"posts": posts, "count": len(posts)})


@scraping_bp.route("/runs")
def get_runs():
    limit = int(request.args.get("limit", 20))
    db = get_db()
    return _ok({"runs": db.get_runs(limit=limit)})
