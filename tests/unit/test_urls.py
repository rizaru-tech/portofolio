import pytest

from portfolio.shared.urls import canonical_url, safe_http_url


@pytest.mark.parametrize("value", (None, "", "/relative", "javascript:alert(1)", "ftp://files.test"))
def test_safe_http_url_rejects_missing_or_unsafe_values(value):
    assert safe_http_url(value) is None


def test_safe_http_url_accepts_absolute_http_urls():
    assert safe_http_url(" https://portfolio.test/cv.pdf ") == "https://portfolio.test/cv.pdf"


def test_canonical_url_requires_a_configured_safe_base():
    assert canonical_url(None, "/") is None
    assert canonical_url("https://portfolio.test", "/") == "https://portfolio.test/"
