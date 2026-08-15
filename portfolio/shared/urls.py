from __future__ import annotations

from urllib.parse import urljoin, urlsplit


def safe_http_url(value: str | None) -> str | None:
    """Return only absolute HTTP(S) URLs suitable for rendered links."""

    if not value:
        return None
    candidate = value.strip()
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return candidate


def canonical_url(base_url: str | None, path: str) -> str | None:
    safe_base = safe_http_url(base_url)
    if not safe_base:
        return None
    return urljoin(f"{safe_base.rstrip('/')}/", path.lstrip("/"))
