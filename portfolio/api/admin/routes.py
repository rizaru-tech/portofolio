from flask import jsonify

from portfolio.api.admin import admin_api_bp
from portfolio.domains.identity_access.auth import admin_login_required


@admin_api_bp.get("")
@admin_api_bp.get("/")
@admin_login_required(api=True)
def status():
    response = jsonify(
        {
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Admin API write endpoints have not been implemented.",
            }
        }
    )
    response.status_code = 501
    return response
