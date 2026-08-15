"""Language registry and resolver for structured Home content."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from portfolio.domains.content.home_en import HOME_EN
from portfolio.domains.content.home_id import HOME_ID
from portfolio.domains.content.home_ja import HOME_JA


HOME_FALLBACK_LANGUAGE = "id"
_HOME_CONTENT = {"id": HOME_ID, "en": HOME_EN, "ja": HOME_JA}


@dataclass(frozen=True)
class ResolvedHomeContent:
    content: dict[str, Any]
    requested_language: str
    effective_language: str
    fallback_used: bool


def resolve_home_content(language: str | None) -> ResolvedHomeContent:
    """Return isolated content for a supported language or the safe fallback."""

    requested_language = (language or HOME_FALLBACK_LANGUAGE).strip().lower()
    effective_language = (
        requested_language
        if requested_language in _HOME_CONTENT
        else HOME_FALLBACK_LANGUAGE
    )
    return ResolvedHomeContent(
        content=deepcopy(_HOME_CONTENT[effective_language]),
        requested_language=requested_language,
        effective_language=effective_language,
        fallback_used=requested_language != effective_language,
    )
