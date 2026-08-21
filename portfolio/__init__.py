from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flask import Flask

from portfolio.config import CONFIG_BY_NAME, BaseConfig, ProductionConfig
from portfolio.domains.identity_access.cli import register_identity_commands
from portfolio.extensions import db, migrate
from portfolio.shared.errors import register_error_handlers
from portfolio.shared.request_context import register_request_context
from portfolio.shared.security import register_security_headers


def create_app(
    config_name: str | type[BaseConfig] | None = None,
    test_config: Mapping[str, Any] | None = None,
) -> Flask:
    """Create and configure one portfolio application instance."""

    app = Flask(__name__, instance_relative_config=True, static_folder=None)

    selected_config = config_name or os.getenv("APP_ENV", "development")
    if isinstance(selected_config, str):
        try:
            config_object = CONFIG_BY_NAME[selected_config]
        except KeyError as exc:
            raise RuntimeError(f"Unknown APP_ENV: {selected_config}") from exc
    else:
        config_object = selected_config

    app.config.from_object(config_object)
    if test_config:
        app.config.update(test_config)

    is_production = issubclass(config_object, ProductionConfig)
    if is_production:
        ProductionConfig.validate(app.config)
    _configure_runtime_paths(app)

    db.init_app(app)
    migrate.init_app(app, db)

    _register_blueprints(app)
    register_identity_commands(app)
    register_request_context(app)
    register_security_headers(app)
    register_error_handlers(app)

    return app


def _configure_runtime_paths(app: Flask) -> None:
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        database_path = instance_path / "portfolio.sqlite3"
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"sqlite:///{database_path.resolve().as_posix()}"
        )

    configured_storage = app.config.get("STORAGE_ROOT")
    storage_root = (
        Path(configured_storage).expanduser()
        if configured_storage
        else Path(app.root_path).parent / "storage"
    ).resolve()
    app.config["STORAGE_ROOT"] = str(storage_root)

    for directory in (storage_root / "media", storage_root / "cv"):
        directory.mkdir(parents=True, exist_ok=True)


def _register_blueprints(app: Flask) -> None:
    from portfolio.admin_web import admin_web_bp, auth_web_bp
    from portfolio.api.admin import admin_api_bp
    from portfolio.api.public import public_api_bp
    from portfolio.public_web import public_web_bp
    from portfolio.shared import shared_bp

    app.register_blueprint(shared_bp)
    app.register_blueprint(public_web_bp)
    app.register_blueprint(admin_web_bp)
    app.register_blueprint(auth_web_bp)
    app.register_blueprint(public_api_bp)
    app.register_blueprint(admin_api_bp)
