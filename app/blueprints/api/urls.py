from app.blueprints.api import api_bp
from app.blueprints.api import views

api_bp.add_url_rule("/health", view_func=views.health, methods=["GET"])
