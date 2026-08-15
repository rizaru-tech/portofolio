import pytest

from portfolio import create_app


def test_testing_config_uses_isolated_in_memory_database(tmp_path):
    app = create_app(
        "testing",
        {"SECRET_KEY": "testing-only", "STORAGE_ROOT": str(tmp_path)},
    )

    assert app.testing is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["SUPPORTED_LANGUAGES"] == ("id", "en", "ja")
    assert app.config["DEFAULT_LANGUAGE"] == "id"
    assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024 * 1024


def test_production_config_fails_closed_without_required_values():
    with pytest.raises(RuntimeError, match="Missing required production configuration"):
        create_app(
            "production",
            {
                "SECRET_KEY": None,
                "SQLALCHEMY_DATABASE_URI": None,
                "STORAGE_ROOT": None,
            },
        )
