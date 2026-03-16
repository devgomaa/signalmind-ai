"""api/controllers/content_controller.py — Sprint 5"""

from flask import Blueprint, jsonify, request
from engine.database import get_db

content_bp = Blueprint("content", __name__)

def _ok(data):  return jsonify({"status": "ok",    "data": data})
def _err(m, c=400): return jsonify({"status": "error", "message": m}), c


@content_bp.route("/content/latest")
def get_latest_content():
    db = get_db()
    content = db.get_latest_content()
    if not content:
        return _err("No content generated yet", 404)
    return _ok(content)


@content_bp.route("/content/history")
def get_content_history():
    limit = int(request.args.get("limit", 10))
    import sqlite3, json
    from engine.config import Config
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, run_id, created_at, substr(strategy,1,200) as strategy_preview "
        "FROM content ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return _ok({"history": [dict(r) for r in rows]})
