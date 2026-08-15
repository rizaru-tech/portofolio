from http import HTTPStatus

from flask import Flask, g, jsonify, make_response, render_template, request

from portfolio.domains.content.home_content import resolve_home_content
from portfolio.shared.localization import localized_url, resolve_language


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return _error_response(
            status=HTTPStatus.NOT_FOUND,
            code="NOT_FOUND",
            message_key="not_found",
        )

    @app.errorhandler(500)
    def internal_server_error(_error):
        return _error_response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message_key="internal_error",
        )


def _error_response(*, status: HTTPStatus, code: str, message_key: str):
    request_id = getattr(g, "request_id", "unavailable")
    language, _invalid = resolve_language(request.args.get("lang"))
    ui = resolve_home_content(language).content["ui"]
    message = ui[f"{message_key}_message"]
    if request.path.startswith("/api/"):
        response = jsonify({"error": {"code": code, "message": message, "request_id": request_id}})
        response.status_code = status.value
        response.headers["Content-Language"] = language
        return response

    response = make_response(
        render_template(
            "shared/error.html",
            status_code=status.value,
            heading=ui[message_key],
            message=message,
            request_id=request_id,
            requested_language=language,
            page_language=language,
            ui=ui,
            localized_url=localized_url,
        ), status.value,
    )
    response.headers["Content-Language"] = language
    return response
