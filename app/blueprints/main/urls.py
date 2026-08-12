from app.blueprints.main import main_bp
from app.blueprints.main import views

main_bp.add_url_rule("/", view_func=views.index, methods=["GET"])
