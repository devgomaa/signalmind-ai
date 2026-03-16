"""api/controllers/workspace_controller.py — Sprint 6"""

from flask import Blueprint, jsonify, request, g
from engine.auth.auth_manager import get_auth
from engine.auth.decorators import require_auth, require_role
from engine.workspace.scheduler import schedule_workspace, unschedule_workspace, get_all_jobs

workspace_bp = Blueprint("workspace", __name__)

def _ok(d):         return jsonify({"status": "ok",    "data": d})
def _err(m, c=400): return jsonify({"status": "error", "message": m}), c


# ── Workspace Settings ────────────────────────────

@workspace_bp.route("/workspace")
@require_auth
def get_workspace():
    ws = get_auth().get_workspace(g.workspace_id)
    if not ws:
        return _err("Workspace not found", 404)
    return _ok(ws)


@workspace_bp.route("/workspace", methods=["PUT"])
@require_role("admin")
def update_workspace():
    data = request.get_json() or {}
    allowed = {"name", "niche", "markets", "schedule_hours"}
    updates = {k: v for k, v in data.items() if k in allowed}

    get_auth().update_workspace(g.workspace_id, **updates)

    # تحديث الـ scheduler لو تغيّر الـ schedule
    if "schedule_hours" in updates:
        schedule_workspace(g.workspace_id, int(updates["schedule_hours"]))

    return _ok({"updated": True})


# ── Competitors ───────────────────────────────────

@workspace_bp.route("/workspace/competitors")
@require_auth
def get_competitors():
    competitors = get_auth().get_competitors(g.workspace_id)
    return _ok({"competitors": competitors, "count": len(competitors)})


@workspace_bp.route("/workspace/competitors", methods=["POST"])
@require_role("admin", "editor")
def add_competitor():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    url  = data.get("url", "").strip()
    ctype = data.get("type", "brand")
    if not name:
        return _err("Competitor name required")
    cid = get_auth().add_competitor(g.workspace_id, name, url, ctype)
    return _ok({"id": cid, "message": "Competitor added"})


@workspace_bp.route("/workspace/competitors/<int:cid>", methods=["DELETE"])
@require_role("admin")
def delete_competitor(cid):
    get_auth().delete_competitor(cid, g.workspace_id)
    return _ok({"deleted": True})


# ── Team Management ───────────────────────────────

@workspace_bp.route("/workspace/team")
@require_auth
def get_team():
    users = get_auth().get_workspace_users(g.workspace_id)
    return _ok({"users": users, "count": len(users)})


@workspace_bp.route("/workspace/team/invite", methods=["POST"])
@require_role("admin")
def invite_member():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    name  = data.get("name", "").strip()
    role  = data.get("role", "editor")
    if not email or not name:
        return _err("email and name required")
    result = get_auth().invite_user(email, name, role, g.workspace_id)
    if not result["ok"]:
        return _err(result["error"], 409)
    return _ok(result)


@workspace_bp.route("/workspace/team/<int:uid>/role", methods=["PUT"])
@require_role("admin")
def update_role(uid):
    data = request.get_json() or {}
    role = data.get("role", "editor")
    get_auth().update_user_role(uid, role, g.workspace_id)
    return _ok({"updated": True})


# ── Scheduler ─────────────────────────────────────

@workspace_bp.route("/workspace/scheduler")
@require_auth
def get_scheduler_status():
    jobs = get_all_jobs()
    ws   = get_auth().get_workspace(g.workspace_id)
    return _ok({
        "schedule_hours": ws.get("schedule_hours", 6),
        "active_jobs":    jobs,
    })


@workspace_bp.route("/workspace/scheduler", methods=["POST"])
@require_role("admin")
def update_schedule():
    data  = request.get_json() or {}
    hours = int(data.get("hours", 6))
    get_auth().update_workspace(g.workspace_id, schedule_hours=hours)
    schedule_workspace(g.workspace_id, hours)
    return _ok({"scheduled": True, "hours": hours})


@workspace_bp.route("/workspace/scheduler/pause", methods=["POST"])
@require_role("admin")
def pause_schedule():
    unschedule_workspace(g.workspace_id)
    return _ok({"paused": True})