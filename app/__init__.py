import os
from datetime import datetime, timezone

from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now(timezone.utc).year}

    from app.blueprints.main import main_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Import models so Flask-Migrate can detect them
    from app import models  # noqa: F401

    return app
