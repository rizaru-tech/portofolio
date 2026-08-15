from flask import Blueprint


admin_web_bp = Blueprint(
    "admin_web",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/admin",
)

from portfolio.admin_web import routes  # noqa: E402, F401
