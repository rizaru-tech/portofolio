from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import timedelta
from typing import Any


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_ROOT = os.getenv("STORAGE_ROOT")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
    PROFILE_IMAGE_URL = os.getenv("PROFILE_IMAGE_URL")
    CV_URL = os.getenv("CV_URL")
    CONTACT_URL = os.getenv("CONTACT_URL")
    OG_IMAGE_URL = os.getenv("OG_IMAGE_URL")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    SUPPORTED_LANGUAGES = ("id", "en", "ja")
    DEFAULT_LANGUAGE = "id"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_PATH = "/"
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv("AUTH_SESSION_LIFETIME_SECONDS", 8 * 60 * 60))
    )
    AUTH_SESSION_LIFETIME_SECONDS = int(
        os.getenv("AUTH_SESSION_LIFETIME_SECONDS", 8 * 60 * 60)
    )
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS = int(
        os.getenv("LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 5)
    )
    LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(
        os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 15 * 60)
    )
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
