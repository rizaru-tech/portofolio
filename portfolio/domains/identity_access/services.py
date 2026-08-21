from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from flask import current_app, request
from sqlalchemy import func, select
from werkzeug.security import check_password_hash, generate_password_hash

from portfolio.domains.identity_access.models import (
    AdminUser,
    AuthSession,
    SecurityAuditEvent,
)
from portfolio.extensions import db


SESSION_TOKEN_KEY = "_admin_session_token"
SESSION_USER_KEY = "_admin_user_id"
_DUMMY_PASSWORD_HASH = generate_password_hash(secrets.token_urlsafe(32))


def utcnow() -> datetime:
    """Return a naive UTC value, matching SQLite's DateTime representation."""

    return datetime.now(UTC).replace(tzinfo=None)


def normalize_email(value: str) -> str:
    return value.strip().lower()


def hash_session_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def source_fingerprint() -> str:
    source = request.remote_addr or "unknown"
    secret = str(current_app.config["SECRET_KEY"]).encode("utf-8")
    return hmac.new(secret, source.encode("utf-8"), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class AuthenticationResult:
    admin_user: AdminUser
    auth_session: AuthSession
    raw_token: str


def verify_credentials(email: str, password: str) -> AdminUser | None:
    normalized = normalize_email(email)
    admin_user = db.session.scalar(
        select(AdminUser).where(AdminUser.email == normalized)
    )
    password_hash = admin_user.password_hash if admin_user else _DUMMY_PASSWORD_HASH
    password_valid = check_password_hash(password_hash, password)
    if not admin_user or not admin_user.is_active or not password_valid:
        return None
    return admin_user


def is_login_rate_limited(source_hash: str, now: datetime | None = None) -> bool:
    now = now or utcnow()
    window_start = now - timedelta(
        seconds=current_app.config["LOGIN_RATE_LIMIT_WINDOW_SECONDS"]
    )
    failures = db.session.scalar(
        select(func.count(SecurityAuditEvent.id)).where(
            SecurityAuditEvent.source_hash == source_hash,
            SecurityAuditEvent.event_type == "login_failed",
            SecurityAuditEvent.created_at >= window_start,
        )
    )
    return int(failures or 0) >= current_app.config["LOGIN_RATE_LIMIT_MAX_ATTEMPTS"]


def record_audit_event(
    event_type: str,
    outcome: str,
    source_hash: str,
    admin_user_id: int | None = None,
) -> SecurityAuditEvent:
    event = SecurityAuditEvent(
        event_type=event_type,
        outcome=outcome,
        source_hash=source_hash,
        admin_user_id=admin_user_id,
    )
    db.session.add(event)
    return event


def record_failed_login(source_hash: str, admin_user_id: int | None = None) -> None:
    record_audit_event("login_failed", "rejected", source_hash, admin_user_id)
    db.session.commit()


def create_auth_session(
    admin_user: AdminUser,
    source_hash: str,
    previous_raw_token: str | None = None,
) -> AuthenticationResult:
    now = utcnow()
    if previous_raw_token:
        previous_session = find_auth_session(previous_raw_token)
        if previous_session and previous_session.revoked_at is None:
            previous_session.revoked_at = now

    raw_token = secrets.token_urlsafe(48)
    auth_session = AuthSession(
        admin_user=admin_user,
        token_hash=hash_session_token(raw_token),
        created_at=now,
        expires_at=now
        + timedelta(seconds=current_app.config["AUTH_SESSION_LIFETIME_SECONDS"]),
        last_seen_at=now,
    )
    admin_user.last_login_at = now
    db.session.add(auth_session)
    record_audit_event("login", "success", source_hash, admin_user.id)
    db.session.commit()
    return AuthenticationResult(admin_user, auth_session, raw_token)


def find_auth_session(raw_token: str) -> AuthSession | None:
    if not raw_token:
        return None
    return db.session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_session_token(raw_token)
        )
    )


def validate_auth_session(raw_token: str | None) -> AuthSession | None:
    if not raw_token:
        return None
    auth_session = find_auth_session(raw_token)
    if not auth_session:
        return None

    now = utcnow()
    if (
        auth_session.revoked_at is not None
        or auth_session.expires_at <= now
        or not auth_session.admin_user.is_active
    ):
        return None

    auth_session.last_seen_at = now
    db.session.commit()
    return auth_session


def revoke_auth_session(
    raw_token: str | None,
    source_hash: str,
    *,
    record_missing: bool = True,
) -> AuthSession | None:
    auth_session = find_auth_session(raw_token) if raw_token else None
    now = utcnow()
    if auth_session and auth_session.revoked_at is None:
        auth_session.revoked_at = now
        record_audit_event(
            "logout", "success", source_hash, auth_session.admin_user_id
        )
    elif record_missing:
        record_audit_event("logout", "no_active_session", source_hash)
    db.session.commit()
    return auth_session
