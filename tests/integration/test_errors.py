def test_unknown_web_page_returns_safe_html_error(client):
    response = client.get("/missing-page")

    assert response.status_code == 404
    assert "Sumber daya tidak ditemukan" in response.get_data(as_text=True)
    assert b"Traceback" not in response.data


def test_unknown_api_returns_safe_json_error(client):
    response = client.get("/api/v1/public/missing")
    payload = response.get_json()

    assert response.status_code == 404
    assert payload["error"]["code"] == "NOT_FOUND"
    assert payload["error"]["request_id"]
    assert "Traceback" not in response.get_data(as_text=True)


def test_internal_error_does_not_expose_exception(client, app):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/_test/internal-error")
    def internal_error():
        raise RuntimeError("internal implementation detail")

    response = client.get("/_test/internal-error")

    assert response.status_code == 500
    assert b"Terjadi kesalahan internal" in response.data
    assert b"internal implementation detail" not in response.data
    assert b"Traceback" not in response.data


def test_visible_error_message_follows_active_language(client):
    response = client.get("/missing-page?lang=ja")
    html = response.get_data(as_text=True)

    assert response.status_code == 404
    assert '<html lang="ja">' in html
    assert "ページが見つかりません" in html
    assert 'href="/?lang=ja"' in html
