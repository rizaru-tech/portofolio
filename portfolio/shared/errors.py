from http import HTTPStatus

from flask import Flask, g, jsonify, render_template, request


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return _error_response(
            status=HTTPStatus.NOT_FOUND,
            code="NOT_FOUND",
            message="Resource tidak ditemukan.",
        )

    @app.errorhandler(500)
    def internal_server_error(_error):
        return _error_response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="Terjadi kesalahan internal.",
        )


def _error_response(*, status: HTTPStatus, code: str, message: str):
    request_id = getattr(g, "request_id", "unavailable")
    if request.path.startswith("/api/"):
        return (
            jsonify(
                {
                    "error": {
                        "code": code,
                        "message": message,
                        "request_id": request_id,
                    }
                }
            ),
            status.value,
        )

    return (
        render_template(
            "shared/error.html",
            status_code=status.value,
            heading=status.phrase,
            message=message,
            request_id=request_id,
        ),
        status.value,
    )
