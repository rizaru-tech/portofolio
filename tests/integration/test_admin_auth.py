from __future__ import annotations

import re
import secrets
from datetime import timedelta

import pytest
from werkzeug.security import generate_password_hash

from portfolio.domains.identity_access.models import (
    AdminUser,
    AuthSession,
    SecurityAuditEvent,
)
from portfolio.domains.identity_access.services import (
    SESSION_TOKEN_KEY,
    hash_session_token,
    utcnow,
)
from portfolio.extensions import db


ADMIN_EMAIL = "test-admin@example.test"
ADMIN_PASSWORD = f"Aa9!{secrets.token_urlsafe(18)}"


@pytest.fixture()
def admin_user(app):
    with app.app_context():
        admin = AdminUser(
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
    return admin_id


def _csrf_from(response) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match
    return match.group(1)


def _login(client, *, email=ADMIN_EMAIL, password=ADMIN_PASSWORD, language="id"):
    csrf = _csrf_from(client.get(f"/login?lang={language}"))
    return client.post(
        f"/login?lang={language}",
        data={
            "csrf_token": csrf,
            "lang": language,
            "email": email,
            "password": password,
        },
    )


def _raw_token(client) -> str:
    with client.session_transaction() as browser_session:
        return browser_session[SESSION_TOKEN_KEY]


def test_login_page_is_direct_only_not_in_public_navigation(client):
    login_response = client.get("/login")
    login_html = login_response.get_data(as_text=True)
    public_html = client.get("/").get_data(as_text=True)

    assert login_response.status_code == 200
    assert '<body class="auth-page">' in login_html
    assert '<main id="main-content" class="auth-layout">' in login_html
    assert '<header' not in login_html
    assert '<footer' not in login_html
    assert 'class="skip-link" href="#main-content"' in login_html
    assert 'class="language-control"' in login_html
    assert 'autocomplete="username"' in login_html
    assert 'autocomplete="current-password"' in login_html
    assert login_response.headers["Cache-Control"] == "no-store"
    assert 'href="/login"' not in public_html


def test_login_styles_keep_full_viewport_and_center_the_auth_card(client):
    css_response = client.get("/admin/static/admin/admin/css/app.css")
    css = css_response.get_data(as_text=True)

    assert css_response.status_code == 200
    assert re.search(r"\.auth-page\s*\{[^}]*min-height:\s*100vh", css, re.DOTALL)
    assert re.search(r"\.auth-layout\s*\{[^}]*align-items:\s*center", css, re.DOTALL)
    assert re.search(r"\.auth-layout\s*\{[^}]*justify-content:\s*center", css, re.DOTALL)
    assert re.search(r"\.auth-layout\s*\{[^}]*min-height:\s*100vh", css, re.DOTALL)


def test_valid_login_creates_hashed_backend_session_and_audit(client, app, admin_user):
    response = _login(client, email=" TEST-ADMIN@EXAMPLE.TEST ")
    raw_token = _raw_token(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/dashboard?lang=id")
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Lax" in response.headers["Set-Cookie"]
    assert "Path=/" in response.headers["Set-Cookie"]
    assert raw_token not in response.get_data(as_text=True)
    with app.app_context():
        auth_session = db.session.scalar(db.select(AuthSession))
        assert auth_session.admin_user_id == admin_user
        assert auth_session.token_hash == hash_session_token(raw_token)
        assert auth_session.token_hash != raw_token
        assert auth_session.expires_at > auth_session.created_at
        assert db.session.scalar(
            db.select(SecurityAuditEvent).where(SecurityAuditEvent.event_type == "login")
        )


def test_invalid_credentials_and_inactive_admin_are_rejected_generically(
    client, app, admin_user
):
    wrong = _login(client, password="wrong-password")
    assert wrong.status_code == 401
    assert "Email atau password tidak valid." in wrong.get_data(as_text=True)
    assert "wrong-password" not in wrong.get_data(as_text=True)

    with app.app_context():
        admin = db.session.get(AdminUser, admin_user)
        admin.is_active = False
        db.session.commit()
    inactive = _login(client)
    assert inactive.status_code == 401
    assert "Email atau password tidak valid." in inactive.get_data(as_text=True)


def test_login_requires_csrf_and_rate_limits_failures(client, app, admin_user):
    no_csrf = client.post(
        "/login", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert no_csrf.status_code == 400

    app.config["LOGIN_RATE_LIMIT_MAX_ATTEMPTS"] = 2
    assert _login(client, password="wrong-1").status_code == 401
    assert _login(client, password="wrong-2").status_code == 401
    limited = _login(client, password=ADMIN_PASSWORD)
    assert limited.status_code == 429
    assert "Terlalu banyak percobaan" in limited.get_data(as_text=True)


def test_each_login_uses_a_new_token_and_other_device_session_remains_active(
    app, admin_user
):
    first_client = app.test_client()
    second_client = app.test_client()
    assert _login(first_client).status_code == 302
    assert _login(second_client).status_code == 302
    first_token = _raw_token(first_client)
    second_token = _raw_token(second_client)

    assert first_token != second_token
    assert first_client.get("/admin/dashboard").status_code == 200
    assert second_client.get("/admin/dashboard").status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(AuthSession.id))) == 2


def test_reauthentication_revokes_the_current_browser_token(client, app, admin_user):
    _login(client)
    previous_token = _raw_token(client)
    csrf = _csrf_from(client.get("/admin/dashboard"))
    with client.session_transaction() as browser_session:
        browser_session["legacy_browser_state"] = "must-not-survive"

    response = client.post(
        "/login",
        data={
            "csrf_token": csrf,
            "lang": "id",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        },
    )
    new_token = _raw_token(client)

    assert response.status_code == 302
    assert new_token != previous_token
    with client.session_transaction() as browser_session:
        assert "legacy_browser_state" not in browser_session
    with app.app_context():
        previous_session = db.session.scalar(
            db.select(AuthSession).where(
                AuthSession.token_hash == hash_session_token(previous_token)
            )
        )
        assert previous_session.revoked_at is not None


def test_external_next_url_is_rejected(client, admin_user):
    csrf = _csrf_from(client.get("/login?next=https://attacker.example"))
    response = client.post(
        "/login",
        data={
            "csrf_token": csrf,
            "next": "https://attacker.example",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/admin/dashboard")


def test_dashboard_rejects_missing_fake_expired_and_revoked_sessions(
    client, app, admin_user
):
    assert client.get("/admin/dashboard").status_code == 302

    with client.session_transaction() as browser_session:
        browser_session[SESSION_TOKEN_KEY] = "fake-token"
    fake = client.get("/admin/dashboard")
    assert fake.status_code == 302
    assert "reason=session_expired" in fake.headers["Location"]

    assert _login(client).status_code == 302
    raw_token = _raw_token(client)
    with app.app_context():
        auth_session = db.session.scalar(
            db.select(AuthSession).where(AuthSession.token_hash == hash_session_token(raw_token))
        )
        auth_session.expires_at = utcnow() - timedelta(seconds=1)
        db.session.commit()
    assert client.get("/admin/dashboard").status_code == 302

    assert _login(client).status_code == 302
    raw_token = _raw_token(client)
    with app.app_context():
        auth_session = db.session.scalar(
            db.select(AuthSession).where(AuthSession.token_hash == hash_session_token(raw_token))
        )
        auth_session.revoked_at = utcnow()
        db.session.commit()
    assert client.get("/admin/dashboard").status_code == 302


def test_admin_api_returns_401_for_invalid_session_and_501_when_authenticated(
    client, admin_user
):
    unauthorized = client.get("/api/v1/admin")
    assert unauthorized.status_code == 401
    assert unauthorized.get_json()["error"]["code"] == "UNAUTHORIZED"

    _login(client)
    assert client.get("/api/v1/admin").status_code == 501


def test_logout_revokes_backend_session_deletes_cookie_and_blocks_old_token(
    client, app, admin_user
):
    _login(client)
    raw_token = _raw_token(client)
    dashboard = client.get("/admin/dashboard")
    csrf = _csrf_from(dashboard)
    response = client.post("/logout", data={"csrf_token": csrf, "lang": "id"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login?lang=id")
    assert "Max-Age=0" in response.headers["Set-Cookie"]
    assert response.headers["Cache-Control"] == "no-store"
    with app.app_context():
        auth_session = db.session.scalar(
            db.select(AuthSession).where(AuthSession.token_hash == hash_session_token(raw_token))
        )
        assert auth_session.revoked_at is not None
        assert db.session.scalar(
            db.select(SecurityAuditEvent).where(SecurityAuditEvent.event_type == "logout")
        )

    assert client.get("/admin/dashboard").status_code == 302
    with client.session_transaction() as browser_session:
        browser_session[SESSION_TOKEN_KEY] = raw_token
    assert client.get("/admin/dashboard").status_code == 302
    assert client.get("/api/v1/admin").status_code == 401


def test_logout_is_post_only_and_requires_csrf(client, admin_user):
    _login(client)
    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 400
    assert client.get("/admin/dashboard").status_code == 200


@pytest.mark.parametrize(
    ("language", "login_text", "dashboard_text"),
    (
        ("id", "Login Admin", "Dashboard"),
        ("en", "Admin login", "Dashboard"),
        ("ja", "管理者ログイン", "ダッシュボード"),
    ),
)
def test_login_and_dashboard_render_all_languages_without_clearing_session(
    client, admin_user, language, login_text, dashboard_text
):
    login_page = client.get(f"/login?lang={language}")
    assert login_text in login_page.get_data(as_text=True)
    assert _login(client, language=language).status_code == 302
    raw_token = _raw_token(client)

    dashboard = client.get(f"/admin/dashboard?lang={language}")
    assert dashboard.status_code == 200
    assert dashboard_text in dashboard.get_data(as_text=True)
    assert f'<html lang="{language}">' in dashboard.get_data(as_text=True)
    assert _raw_token(client) == raw_token


def test_authenticated_user_opening_login_is_redirected(client, admin_user):
    _login(client)
    response = client.get("/login?lang=en")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/dashboard?lang=en")
