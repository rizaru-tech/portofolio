from flask import jsonify

from portfolio.api.admin import admin_api_bp


@admin_api_bp.get("")
@admin_api_bp.get("/")
def status():
    response = jsonify(
        {
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Admin API authentication has not been implemented.",
            }
        }
    )
    response.status_code = 501
    return response
