import pytest


@pytest.mark.parametrize("route", ["/", "/projects", "/cv", "/blog"])
def test_public_foundation_routes_are_available(client, route):
    response = client.get(route)

    assert response.status_code == 200
    assert b"<main" in response.data


def test_admin_route_is_an_explicit_non_authenticated_placeholder(client):
    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Authentication dan content management belum diimplementasikan" in response.data


def test_public_health_endpoint_has_stable_shape(client):
    response = client.get("/api/v1/public/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": {"service": "portfolio", "status": "ok"}
    }


def test_admin_api_has_no_write_capability(client):
    get_response = client.get("/api/v1/admin")
    post_response = client.post("/api/v1/admin", json={})

    assert get_response.status_code == 501
    assert post_response.status_code == 405
