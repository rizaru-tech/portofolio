from __future__ import annotations

import getpass
import re

import click
from flask import Flask
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from portfolio.domains.identity_access.models import AdminUser
from portfolio.domains.identity_access.services import normalize_email
from portfolio.extensions import db


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_password_strength(password: str) -> list[str]:
    failures = []
    if len(password) < 12:
        failures.append("at least 12 characters")
    if not any(character.islower() for character in password):
        failures.append("a lowercase letter")
    if not any(character.isupper() for character in password):
        failures.append("an uppercase letter")
    if not any(character.isdigit() for character in password):
        failures.append("a number")
    if not any(not character.isalnum() for character in password):
        failures.append("a symbol")
    return failures


def register_identity_commands(app: Flask) -> None:
    @app.cli.command("create-admin")
    @click.option("--email", required=True, help="Email address for the admin account.")
    def create_admin(email: str) -> None:
        normalized_email = normalize_email(email)
        if not EMAIL_PATTERN.fullmatch(normalized_email):
            raise click.ClickException("Provide a valid email address.")

        existing = db.session.scalar(
            select(AdminUser.id).where(AdminUser.email == normalized_email)
        )
        if existing is not None:
            raise click.ClickException("An admin account with that email already exists.")

        password = getpass.getpass("New password: ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            raise click.ClickException("Password confirmation does not match.")
        failures = validate_password_strength(password)
        if failures:
            requirements = ", ".join(failures)
            raise click.ClickException(f"Password must include {requirements}.")

        admin_user = AdminUser(
            email=normalized_email,
            password_hash=generate_password_hash(password),
            is_active=True,
        )
        db.session.add(admin_user)
        db.session.commit()
        click.echo("Admin account created.")

