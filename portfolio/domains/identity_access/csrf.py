from __future__ import annotations

import hmac
import secrets

from flask import request, session


CSRF_SESSION_KEY = "_csrf_token"


def get_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not isinstance(token, str) or not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def valid_csrf_token() -> bool:
    expected = session.get(CSRF_SESSION_KEY)
    supplied = request.form.get("csrf_token", "")
    return (
        isinstance(expected, str)
        and bool(expected)
        and bool(supplied)
        and hmac.compare_digest(expected, supplied)
    )

