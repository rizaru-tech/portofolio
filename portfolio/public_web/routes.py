from flask import current_app, make_response, render_template, request

from portfolio.domains.content.home_content import resolve_home_content
from portfolio.public_web import public_web_bp
from portfolio.shared.localization import localized_url, resolve_language
from portfolio.shared.urls import canonical_url, safe_http_url


PAGES = {
    "projects": {
        "id": ("Proyek", "Proyek", "Daftar proyek lengkap sedang disiapkan."),
        "en": ("Projects", "Projects", "The complete project collection is being prepared."),
        "ja": ("プロジェクト", "プロジェクト", "プロジェクト一覧は現在準備中です。"),
    },
    "cv": {
        "id": ("CV", "CV", "Halaman CV dan fitur unduh sedang disiapkan."),
        "en": ("CV", "CV", "The CV page and download are being prepared."),
        "ja": ("CV", "CV", "CVページとダウンロード機能は現在準備中です。"),
    },
    "blog": {
        "id": ("Blog", "Blog", "Daftar dan artikel Blog sedang disiapkan."),
        "en": ("Blog", "Blog", "The Blog index and articles are being prepared."),
        "ja": ("ブログ", "ブログ", "ブログ記事は現在準備中です。"),
    },
}


def _language_context():
    requested = request.args.get("lang")
    language, invalid = resolve_language(requested)
    resolved = resolve_home_content(language)
    return language, invalid, resolved


def _response(template: str, *, language: str, **context):
    response = make_response(render_template(template, page_language=language, **context))
    response.headers["Content-Language"] = language
    return response


@public_web_bp.get("/")
def home():
    language, invalid, resolved = _language_context()
    ui = resolved.content["ui"]
    asset_urls = {
        "profile_image": safe_http_url(current_app.config.get("PROFILE_IMAGE_URL")),
        "cv": safe_http_url(current_app.config.get("CV_URL")),
        "contact": safe_http_url(current_app.config.get("CONTACT_URL")),
        "og_image": safe_http_url(current_app.config.get("OG_IMAGE_URL")),
    }
    base_url = current_app.config.get("PUBLIC_BASE_URL")
    canonical = canonical_url(base_url, localized_url("public_web.home", language))
    alternates = {
        code: canonical_url(base_url, localized_url("public_web.home", code))
        for code in current_app.config["SUPPORTED_LANGUAGES"]
    }
    return _response(
        "public/home.html", language=language, home=resolved.content, ui=ui,
        requested_language=language, fallback_used=invalid,
        canonical_url=canonical, alternate_urls=alternates, assets=asset_urls,
        localized_url=localized_url,
    )


@public_web_bp.get("/projects")
def projects():
    return _render_page("projects")


@public_web_bp.get("/cv")
def cv():
    return _render_page("cv")


@public_web_bp.get("/blog")
def blog():
    return _render_page("blog")


def _render_page(page_name: str):
    language, _invalid, resolved = _language_context()
    ui = resolved.content["ui"]
    title, heading, summary = PAGES[page_name][language]
    return _response(
        "public/page.html", language=language,
        page={"title": title, "heading": heading, "summary": summary},
        requested_language=language, ui=ui, localized_url=localized_url,
    )
