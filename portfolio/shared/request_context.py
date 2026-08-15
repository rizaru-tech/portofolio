from uuid import uuid4

from flask import Flask, g, request


def register_request_context(app: Flask) -> None:
    @app.before_request
    def assign_request_id() -> None:
        candidate = request.headers.get("X-Request-ID", "")
        g.request_id = candidate[:128] if candidate else uuid4().hex

    @app.after_request
    def expose_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response
