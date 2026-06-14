import os
from flask import Flask, send_file, send_from_directory, abort
from flask_cors import CORS
from config.database import init_db
from routes.auth import auth_bp
from routes.bookings import bookings_bp
from routes.home_visits import home_visits_bp
from routes.beard_styles import beard_styles_bp
from routes.salons import salons_bp
from routes.ai_scans import ai_scans_bp
from routes.dashboard import dashboard_bp
from config.settings import Config


def _serve_html(app, filename):
    path = os.path.join(app.root_path, "static", filename)
    if not os.path.exists(path):
        abort(404, description=f"Frontend file '{filename}' not found in static/.")
    return send_file(path, mimetype="text/html")


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_db(app)

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(bookings_bp,     url_prefix="/api/bookings")
    app.register_blueprint(home_visits_bp,  url_prefix="/api/home-visits")
    app.register_blueprint(beard_styles_bp, url_prefix="/api/beard-styles")
    app.register_blueprint(salons_bp,       url_prefix="/api/salons")
    app.register_blueprint(ai_scans_bp,     url_prefix="/api/ai-scans")
    app.register_blueprint(dashboard_bp,    url_prefix="/api/dashboard")

    @app.route("/")
    def index():
        return _serve_html(app, "groomx_v6.html")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory("static", filename)

    @app.route("/api/docs")
    def docs():
        return {"version": "6.0", "status": "running"}

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 50)
    print("  GroomX Backend Starting...")
    print("  http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
