from flask import Flask

from portfolio import create_app


def test_application_factory_creates_flask_app(tmp_path):
    app = create_app(
        "testing",
        {"SECRET_KEY": "testing-only", "STORAGE_ROOT": str(tmp_path)},
    )

    assert isinstance(app, Flask)
    assert {"public_web", "admin_web", "public_api", "admin_api"}.issubset(
        app.blueprints
    )
