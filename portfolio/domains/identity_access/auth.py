from __future__ import annotations

from functools import wraps
from urllib.parse import urlsplit

from flask import g, jsonify, redirect, request, session, url_for

from portfolio.domains.identity_access.services import (
    SESSION_TOKEN_KEY,
    validate_auth_session,
)
from portfolio.shared.localization import resolve_language


def safe_next_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value)
    if (
        parsed.scheme
        or parsed.netloc
        or not value.startswith("/")
        or value.startswith("//")
        or "\\" in value
    ):
        return None
    return value


def admin_login_required(view=None, *, api: bool = False):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped(*args, **kwargs):
            raw_token = session.get(SESSION_TOKEN_KEY)
            auth_session = validate_auth_session(raw_token)
            if not auth_session:
                had_token = bool(raw_token)
                session.clear()
                if api:
                    response = jsonify(
                        {
                            "error": {
                                "code": "UNAUTHORIZED",
                                "message": "Authentication required.",
                            }
                        }
                    )
                    response.status_code = 401
                    response.headers["Cache-Control"] = "no-store"
                    return response

                language, _invalid = resolve_language(request.args.get("lang"))
                values = {"lang": language, "next": request.full_path.rstrip("?")}
                if had_token:
                    values["reason"] = "session_expired"
                response = redirect(url_for("auth_web.login", **values))
                response.headers["Cache-Control"] = "no-store"
                return response

            g.current_admin = auth_session.admin_user
            g.current_auth_session = auth_session
            return view_function(*args, **kwargs)

        return wrapped

    return decorator(view) if view is not None else decorator
