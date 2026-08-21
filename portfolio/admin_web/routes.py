from __future__ import annotations

from flask import (
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import select

from portfolio.admin_web import admin_web_bp, auth_web_bp
from portfolio.domains.identity_access.auth import (
    admin_login_required,
    safe_next_url,
)
from portfolio.domains.identity_access.csrf import get_csrf_token, valid_csrf_token
from portfolio.domains.identity_access.localization import auth_ui
from portfolio.domains.identity_access.models import AdminUser
from portfolio.domains.identity_access.services import (
    SESSION_TOKEN_KEY,
    SESSION_USER_KEY,
    create_auth_session,
    is_login_rate_limited,
    normalize_email,
    record_failed_login,
    revoke_auth_session,
    source_fingerprint,
    validate_auth_session,
    verify_credentials,
)
from portfolio.extensions import db
from portfolio.shared.localization import resolve_language


def _language_context():
    explicit = request.form.get("lang") if request.method == "POST" else None
    language, _invalid = resolve_language(explicit or request.args.get("lang"))
    return language, auth_ui(language)


def _no_store(response):
    language, _invalid = resolve_language(
        request.form.get("lang") or request.args.get("lang")
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Language"] = language
    return response


def _render_login(*, error: str | None = None, status: int = 200):
    language, ui = _language_context()
    next_url = safe_next_url(request.form.get("next") or request.args.get("next"))
    response = make_response(
        render_template(
            "admin/login.html",
            page_language=language,
            requested_language=language,
            ui=ui,
            csrf_token=get_csrf_token(),
            next_url=next_url,
            error=error,
            reason=request.args.get("reason"),
        ),
        status,
    )
    return _no_store(response)


@admin_web_bp.get("")
@admin_web_bp.get("/")
@admin_login_required
def index():
    language, _ui = _language_context()
    return redirect(url_for("admin_web.dashboard", lang=language))


@admin_web_bp.get("/dashboard")
@admin_login_required
def dashboard():
    language, ui = _language_context()
    response = make_response(
        render_template(
            "admin/dashboard.html",
            page_language=language,
            requested_language=language,
            ui=ui,
            current_admin=g.current_admin,
            csrf_token=get_csrf_token(),
        )
    )
    return _no_store(response)


@auth_web_bp.get("/login")
def login():
    auth_session = validate_auth_session(session.get(SESSION_TOKEN_KEY))
    if auth_session:
        language, _ui = _language_context()
        return _no_store(redirect(url_for("admin_web.dashboard", lang=language)))
    if session.get(SESSION_TOKEN_KEY):
        session.clear()
    return _render_login()


@auth_web_bp.post("/login")
def login_submit():
    language, ui = _language_context()
    if not valid_csrf_token():
        return _render_login(error=ui["csrf_error"], status=400)

    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    if not email or not password:
        return _render_login(error=ui["required_fields"], status=400)

    source_hash = source_fingerprint()
    if is_login_rate_limited(source_hash):
        return _render_login(error=ui["rate_limited"], status=429)

    admin_user = verify_credentials(email, password)
    if not admin_user:
        known_user_id = db.session.scalar(
            select(AdminUser.id).where(AdminUser.email == email)
        )
        record_failed_login(source_hash, known_user_id)
        return _render_login(error=ui["invalid_credentials"], status=401)

    previous_raw_token = session.get(SESSION_TOKEN_KEY)
    session.clear()
    result = create_auth_session(admin_user, source_hash, previous_raw_token)
    session.permanent = True
    session[SESSION_TOKEN_KEY] = result.raw_token
    session[SESSION_USER_KEY] = result.admin_user.id
    get_csrf_token()

    next_url = safe_next_url(request.form.get("next"))
    target = next_url or url_for("admin_web.dashboard", lang=language)
    return _no_store(redirect(target))


@auth_web_bp.post("/logout")
def logout():
    language, ui = _language_context()
    if not valid_csrf_token():
        response = make_response(
            render_template(
                "admin/csrf_error.html",
                page_language=language,
                requested_language=language,
                ui=ui,
            ),
            400,
        )
        return _no_store(response)

    raw_token = session.get(SESSION_TOKEN_KEY)
    revoke_auth_session(raw_token, source_fingerprint())
    session.clear()
    return _no_store(redirect(url_for("auth_web.login", lang=language)))
