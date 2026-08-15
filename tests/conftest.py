import pytest

from portfolio import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app(
        "testing",
        {
            "SECRET_KEY": "testing-only",
            "STORAGE_ROOT": str(tmp_path / "storage"),
        },
    )


@pytest.fixture()
def client(app):
    return app.test_client()
