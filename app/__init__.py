import os
from datetime import datetime, timezone

from flask import Flask

from app.config import config_by_name
from app.extensions import csrf, db, login_manager, mail, migrate


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    if not app.config.get("UPLOAD_FOLDER"):
        app.config["UPLOAD_FOLDER"] = os.path.join(
            app.root_path, "static", "uploads", "lawyers"
        )
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        from app.models import User

        if not user_id:
            return None
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now(timezone.utc).year}

    from app.blueprints.main import main_bp
    from app.blueprints.api import api_bp
    from app.cli import register_cli

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    register_cli(app)

    from app import models  # noqa: F401

    return app
