from flask import Blueprint


public_api_bp = Blueprint("public_api", __name__, url_prefix="/api/v1/public")

from portfolio.api.public import routes  # noqa: E402, F401
