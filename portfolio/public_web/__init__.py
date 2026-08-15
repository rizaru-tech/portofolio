from flask import Blueprint


public_web_bp = Blueprint(
    "public_web",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/public",
)

from portfolio.public_web import routes  # noqa: E402, F401
