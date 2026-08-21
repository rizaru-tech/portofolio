import pytest

from portfolio import create_app
from portfolio.extensions import db


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        "testing",
        {
            "SECRET_KEY": "testing-only",
            "STORAGE_ROOT": str(tmp_path / "storage"),
        },
    )
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
