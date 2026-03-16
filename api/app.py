"""
api/app.py — Sprint 6 (updated)
"""

import os
from flask import Flask
from flask_cors import CORS

from api.routes import register_routes
from engine.config import Config
from engine.utils.logger import get_logger

logger = get_logger("App")


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../dashboard/templates",
        static_folder="../dashboard/static",
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["JSON_SORT_KEYS"] = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    register_routes(app)

    # ── Auth tables ───────────────────────────────
    from engine.auth.auth_manager import get_auth
    get_auth()   # يُنشئ الـ tables تلقائياً

    # ── Scheduler ─────────────────────────────────
    from engine.workspace.scheduler import init_all_workspace_schedules
    init_all_workspace_schedules()

    logger.info("Flask app created (Sprint 6)")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=Config.DEBUG,
    )