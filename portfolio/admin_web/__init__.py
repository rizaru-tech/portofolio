from flask import Blueprint


admin_web_bp = Blueprint(
    "admin_web",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/admin",
)

auth_web_bp = Blueprint(
    "auth_web",
    __name__,
    template_folder="templates",
)

from portfolio.admin_web import routes  # noqa: E402, F401
