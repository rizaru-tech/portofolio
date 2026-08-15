from flask import jsonify

from portfolio.api.public import public_api_bp


@public_api_bp.get("/health")
def health():
    return jsonify({"data": {"service": "portfolio", "status": "ok"}})
