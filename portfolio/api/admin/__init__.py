from flask import Blueprint


admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/api/v1/admin")

from portfolio.api.admin import routes  # noqa: E402, F401
