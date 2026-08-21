import pytest


@pytest.mark.parametrize("route", ["/", "/projects", "/cv", "/blog"])
def test_public_foundation_routes_are_available(client, route):
    response = client.get(route)

    assert response.status_code == 200
    assert b"<main" in response.data


def test_admin_route_requires_authentication(client):
    response = client.get("/admin")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_public_health_endpoint_has_stable_shape(client):
    response = client.get("/api/v1/public/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": {"service": "portfolio", "status": "ok"}
    }


def test_admin_api_requires_authentication_and_has_no_write_capability(client):
    get_response = client.get("/api/v1/admin")
    post_response = client.post("/api/v1/admin", json={})

    assert get_response.status_code == 401
    assert post_response.status_code == 405
