"""api/controllers/auth_controller.py — Sprint 6"""

from flask import Blueprint, jsonify, request, g
from engine.auth.auth_manager import get_auth
from engine.auth.decorators import require_auth
# جديد
from engine.workspace.niche_config import NICHES, MARKETS, NICHE_LABELS, MARKET_LABELS
auth_bp = Blueprint("auth", __name__)

def _ok(d):      return jsonify({"status": "ok",    "data": d})
def _err(m, c=400): return jsonify({"status": "error", "message": m}), c


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name     = data.get("name", "").strip()
    niche    = data.get("niche", "tech")
    markets  = data.get("markets", ["global"])
    ws_name  = data.get("workspace_name", f"{name}'s Workspace")

    if not email or not password or not name:
        return _err("email, password, name required")
    if len(password) < 6:
        return _err("Password must be at least 6 characters")
    if niche not in NICHES:
        return _err(f"Invalid niche. Choose from: {NICHES}")

    result = get_auth().register(email, password, name, ws_name, niche, markets)
    if not result["ok"]:
        return _err(result["error"], 409)
    return _ok(result)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return _err("email and password required")
    result = get_auth().login(email, password)
    if not result["ok"]:
        return _err(result["error"], 401)
    return _ok(result)


@auth_bp.route("/auth/me")
@require_auth
def me():
    user = get_auth().get_user(g.user_id)
    if not user:
        return _err("User not found", 404)
    ws = get_auth().get_workspace(g.workspace_id)
    return _ok({"user": user, "workspace": ws})


@auth_bp.route("/auth/niches")
def get_niches():
    return _ok([{"value": k, "label": v} for k, v in NICHE_LABELS.items()])


@auth_bp.route("/auth/markets")
def get_markets():
    return _ok([{"value": k, "label": v} for k, v in MARKET_LABELS.items()])
