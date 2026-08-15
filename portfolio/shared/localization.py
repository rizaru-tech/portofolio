from __future__ import annotations

from flask import current_app


def resolve_language(explicit_language: str | None = None) -> tuple[str, bool]:
    """Resolve the existing explicit query preference, then configured default."""

    supported = current_app.config["SUPPORTED_LANGUAGES"]
    default = current_app.config["DEFAULT_LANGUAGE"]
    candidate = (explicit_language or default).strip().lower()
    return (candidate, False) if candidate in supported else (default, True)


def localized_url(endpoint: str, language: str, **values) -> str:
    from flask import url_for

    return url_for(endpoint, lang=language, **values)
