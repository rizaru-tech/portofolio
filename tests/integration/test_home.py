from portfolio import create_app
import pytest


@pytest.mark.parametrize(
    ("language", "title", "headings"),
    (
        ("id", "Software Engineer", ("Tentang Saya", "Ringkasan Pengalaman", "Proyek Unggulan", "Tugas Akhir", "Keahlian Teknis", "Pendidikan")),
        ("en", "Software Engineer", ("About Me", "Experience Highlights", "Featured Projects", "Final-Year Project", "Technical Skills", "Education")),
        ("ja", "ソフトウェアエンジニア", ("私について", "主な職務経験", "注目プロジェクト", "卒業制作", "技術スキル", "学歴")),
    ),
)
def test_home_is_complete_in_each_supported_language(client, language, title, headings):
    response = client.get(f"/?lang={language}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.headers["Content-Language"] == language
    assert f'<html lang="{language}">' in html
    assert title in html
    assert all(heading in html for heading in headings)
    assert html.count("<section") == 9
    assert html.count("<option value=") == 3
    assert f'<option value="{language}" selected>' in html
    assert "home." not in html and "ui." not in html


@pytest.mark.parametrize("route", ("/", "/projects", "/cv", "/blog"))
def test_language_query_is_preserved_across_public_navigation(client, route):
    html = client.get(f"{route}?lang=ja").get_data(as_text=True)

    assert 'href="/?lang=ja"' in html
    assert 'href="/projects?lang=ja"' in html
    assert 'href="/cv?lang=ja"' in html
    assert 'href="/blog?lang=ja"' in html
    assert '<option value="ja" selected>' in html
    assert 'public/js/app.js?v=2' in html


def test_language_selector_script_navigates_with_selected_query(client):
    response = client.get("/static/public/public/js/app.js?v=2")
    script = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'searchParams.set("lang", languageSelector.value)' in script
    assert "window.location.assign" in script


def test_language_selector_hides_apply_fallback_after_javascript_loads(client):
    html = client.get("/?lang=id").get_data(as_text=True)
    script = client.get("/static/public/public/js/app.js?v=2").get_data(as_text=True)

    assert 'data-language-selector' in html
    assert 'data-language-submit' in html
    assert "languageSubmit.hidden = true" in script


def test_public_header_uses_sticky_positioning(client):
    response = client.get("/static/shared/shared/css/base.css")
    css = response.get_data(as_text=True)

    assert response.status_code == 200
    assert ".site-header" in css
    assert "position: sticky" in css
    assert "top: 0" in css


@pytest.mark.parametrize("language", ("id", "en", "ja"))
def test_long_skill_lists_use_balanced_two_column_modifier(client, language):
    html = client.get(f"/?lang={language}").get_data(as_text=True)

    # Front-end, back-end, and tools have more than six entries; narrow screens stay single-column.
    assert html.count("skill-list skill-list-two-columns") == 3


def test_unsupported_language_uses_safe_indonesian_fallback(client):
    response = client.get("/?lang=xx")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.headers["Content-Language"] == "id"
    assert '<html lang="id">' in html
    assert "Tentang Saya" in html
    assert "Terjemahan yang diminta tidak tersedia" in html
    assert "xx" not in html.lower()


def test_navigation_title_buttons_and_metadata_follow_japanese(client):
    html = client.get("/?lang=ja").get_data(as_text=True)

    assert "<title>Muhammad Rizal Muhaimin | ソフトウェアエンジニア</title>" in html
    assert 'name="description" content="モダンWeb開発' in html
    assert ">ホーム</a>" in html and ">プロジェクト</a>" in html and ">ブログ</a>" in html
    assert "プロジェクトを見る" in html and "お問い合わせ" in html
    assert "About Me" not in html and "Featured Projects" not in html


def test_home_renders_required_sections_and_positioning(client):
    response = client.get("/?lang=en")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert html.count("<h1") == 1
    assert "Muhammad Rizal Muhaimin | Software Engineer" in html
    assert "Software Engineer building reliable and user-focused digital products." in html
    for heading in (
        "About Me", "Experience Highlights", "Featured Projects", "Final-Year Project",
        "Technical Skills", "Currently Learning", "Education", "What I’m Building Toward",
        "Let’s Build Something Meaningful",
    ):
        assert heading in html
    assert "AI Engineer" not in html
    assert "Robotics Engineer" not in html
    assert "example.com" not in html


def test_home_renders_japanese_without_fallback(client):
    response = client.get("/?lang=ja")
    html = response.get_data(as_text=True)

    assert '<html lang="ja">' in html
    assert "主な職務経験" in html
    assert '<option value="ja" selected>' in html
    assert "日本語" in html


def test_home_uses_accessible_placeholders_when_assets_are_unconfigured(client):
    html = client.get("/?lang=en").get_data(as_text=True)

    assert "Professional photo placeholder" in html
    assert html.count('aria-disabled="true"') == 3
    assert "CV_URL" in html
    assert "CONTACT_URL" in html
    assert 'rel="canonical"' not in html


def test_home_renders_only_configured_safe_assets(tmp_path):
    app = create_app("testing", {
        "SECRET_KEY": "testing-only",
        "STORAGE_ROOT": str(tmp_path / "storage"),
        "PUBLIC_BASE_URL": "https://portfolio.test",
        "PROFILE_IMAGE_URL": "https://cdn.test/profile.jpg",
        "CV_URL": "https://cdn.test/rizal-cv.pdf",
        "CONTACT_URL": "mailto:unsafe@example.test",
        "OG_IMAGE_URL": "https://cdn.test/share.jpg",
    })
    html = app.test_client().get("/?lang=en").get_data(as_text=True)

    assert '<link rel="canonical" href="https://portfolio.test/?lang=en">' in html
    assert 'src="https://cdn.test/profile.jpg"' in html
    assert 'href="https://cdn.test/rizal-cv.pdf"' in html
    assert 'content="https://cdn.test/share.jpg"' in html
    assert "mailto:unsafe@example.test" not in html
    assert "Contact placeholder" in html
