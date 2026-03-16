"""api/routes.py — Sprint 7"""

from flask import render_template
from api.controllers.trend_controller      import trends_bp
from api.controllers.content_controller    import content_bp
from api.controllers.scraping_controller   import scraping_bp
from api.controllers.pipeline_controller   import pipeline_bp
from api.controllers.auth_controller       import auth_bp
from api.controllers.workspace_controller  import workspace_bp
from api.controllers.content_studio_controller import studio_bp   # Sprint 7


def register_routes(app):

    app.register_blueprint(trends_bp,    url_prefix="/api")
    app.register_blueprint(content_bp,   url_prefix="/api")
    app.register_blueprint(scraping_bp,  url_prefix="/api")
    app.register_blueprint(pipeline_bp,  url_prefix="/api")
    app.register_blueprint(auth_bp,      url_prefix="/api")
    app.register_blueprint(workspace_bp, url_prefix="/api")
    app.register_blueprint(studio_bp,    url_prefix="/api")   # Sprint 7

    @app.route("/")
    def index():
        return render_template("dashboard.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/trends")
    def trends_page():
        return render_template("trends.html")

    @app.route("/content")
    def content_page():
        return render_template("content.html")

    @app.route("/health")
    def health():
        return {"status": "ok", "version": "3.0.0", "sprint": "7"}