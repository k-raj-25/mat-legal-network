from app.blueprints.main import main_bp
from app.blueprints.main import views

main_bp.add_url_rule("/", view_func=views.index, methods=["GET"])
main_bp.add_url_rule("/find-lawyers", view_func=views.find_lawyers, methods=["GET"])
main_bp.add_url_rule(
    "/lawyers/<slug>",
    view_func=views.lawyer_profile,
    methods=["GET"],
)
main_bp.add_url_rule("/about", view_func=views.about, methods=["GET"])
main_bp.add_url_rule("/contact", view_func=views.contact, methods=["GET", "POST"])
main_bp.add_url_rule("/login", view_func=views.login, methods=["GET", "POST"])
main_bp.add_url_rule("/logout", view_func=views.logout, methods=["POST"])
main_bp.add_url_rule("/signup", view_func=views.signup, methods=["GET"])
main_bp.add_url_rule(
    "/register-lawyer",
    view_func=views.register_lawyer,
    methods=["GET", "POST"],
)
main_bp.add_url_rule("/account", view_func=views.account, methods=["GET"])
main_bp.add_url_rule(
    "/account/reapply",
    view_func=views.reapply,
    methods=["GET", "POST"],
)
main_bp.add_url_rule("/privacy", view_func=views.privacy, methods=["GET"])
main_bp.add_url_rule("/terms", view_func=views.terms, methods=["GET"])
