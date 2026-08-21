import secrets

from portfolio.domains.identity_access.models import AdminUser
from portfolio.extensions import db


def test_create_admin_cli_hashes_password_and_normalizes_email(app, monkeypatch):
    test_password = f"Aa9!{secrets.token_urlsafe(18)}"
    responses = iter((test_password, test_password))
    monkeypatch.setattr("getpass.getpass", lambda _prompt: next(responses))

    result = app.test_cli_runner().invoke(
        args=["create-admin", "--email", "  ADMIN@Example.COM "]
    )

    assert result.exit_code == 0
    assert "Admin account created." in result.output
    assert test_password not in result.output
    with app.app_context():
        admin = db.session.scalar(db.select(AdminUser))
        assert admin.email == "admin@example.com"
        assert admin.password_hash != test_password


def test_create_admin_cli_refuses_duplicate_without_overwriting(app, monkeypatch):
    with app.app_context():
        db.session.add(AdminUser(email="admin@example.com", password_hash="existing-hash"))
        db.session.commit()

    monkeypatch.setattr(
        "getpass.getpass",
        lambda _prompt: (_ for _ in ()).throw(AssertionError("must not prompt")),
    )
    result = app.test_cli_runner().invoke(
        args=["create-admin", "--email", "ADMIN@example.com"]
    )

    assert result.exit_code != 0
    assert "already exists" in result.output
    with app.app_context():
        admin = db.session.scalar(db.select(AdminUser))
        assert admin.password_hash == "existing-hash"
