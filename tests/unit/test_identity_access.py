import secrets

from werkzeug.security import generate_password_hash

from portfolio.domains.identity_access.cli import validate_password_strength
from portfolio.domains.identity_access.models import AdminUser
from portfolio.domains.identity_access.services import normalize_email, verify_credentials
from portfolio.extensions import db


def test_email_is_normalized_and_password_is_stored_as_hash(app):
    raw_password = f"Aa9!{secrets.token_urlsafe(18)}"
    admin = AdminUser(
        email=normalize_email("  ADMIN@Example.COM "),
        password_hash=generate_password_hash(raw_password),
    )
    with app.app_context():
        db.session.add(admin)
        db.session.commit()
        stored = db.session.get(AdminUser, admin.id)

        assert stored.email == "admin@example.com"
        assert stored.password_hash != raw_password
        assert raw_password not in stored.password_hash
        assert verify_credentials(" ADMIN@EXAMPLE.COM ", raw_password) == stored
        assert verify_credentials("admin@example.com", "wrong-password") is None


def test_password_strength_requires_length_and_character_classes():
    assert validate_password_strength("short")
    assert validate_password_strength("longlowercaseonly")
    assert validate_password_strength(f"Aa9!{secrets.token_urlsafe(18)}") == []
