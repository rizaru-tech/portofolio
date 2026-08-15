from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_ROOT = os.getenv("STORAGE_ROOT")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    SUPPORTED_LANGUAGES = ("id", "en", "ja")
    DEFAULT_LANGUAGE = "id"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @staticmethod
    def validate(config: Mapping[str, Any]) -> None:
        required = ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "STORAGE_ROOT")
        missing = [key for key in required if not config.get(key)]
        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"Missing required production configuration: {names}")


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
