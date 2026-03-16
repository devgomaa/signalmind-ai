"""engine/auth/decorators.py — Sprint 6"""

from functools import wraps
from flask import request, jsonify
from engine.auth.auth_manager import get_auth


def _get_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return request.cookies.get("token")


def require_auth(f):
    """يتحقق إن الـ token صح ويضيف g.user و g.workspace_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g
        token = _get_token()
        if not token:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        payload = get_auth().verify_token(token)
        if not payload:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
        g.user_id      = payload["user_id"]
        g.workspace_id = payload["workspace_id"]
        g.role         = payload.get("role", "viewer")
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """يتحقق من الـ role — مثال: @require_role('admin', 'editor')"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import g
            token = _get_token()
            if not token:
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            payload = get_auth().verify_token(token)
            if not payload:
                return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
            if payload.get("role") not in roles:
                return jsonify({"status": "error", "message": "Insufficient permissions"}), 403
            from flask import g
            g.user_id      = payload["user_id"]
            g.workspace_id = payload["workspace_id"]
            g.role         = payload["role"]
            return f(*args, **kwargs)
        return decorated
    return decorator
