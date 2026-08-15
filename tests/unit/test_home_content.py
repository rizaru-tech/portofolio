from portfolio.domains.content.home_content import resolve_home_content
from portfolio.domains.content.home_en import HOME_EN
from portfolio.domains.content.home_id import HOME_ID
from portfolio.domains.content.home_ja import HOME_JA


def test_english_home_content_is_used_directly():
    resolved = resolve_home_content("en")

    assert resolved.effective_language == "en"
    assert resolved.fallback_used is False
    assert resolved.content["hero"]["headline"].startswith("Software Engineer")


def test_all_supported_languages_have_complete_content():
    for language in ("id", "en", "ja"):
        resolved = resolve_home_content(language)
        assert resolved.requested_language == language
        assert resolved.effective_language == language
        assert resolved.fallback_used is False


def test_unsupported_language_falls_back_to_indonesian():
    resolved = resolve_home_content("unknown")
    assert resolved.effective_language == "id"
    assert resolved.fallback_used is True


def test_resolved_content_is_an_isolated_copy():
    first = resolve_home_content("en")
    first.content["hero"]["headline"] = "Changed"

    assert resolve_home_content("en").content["hero"]["headline"] != "Changed"


def test_positioning_does_not_claim_ai_or_robotics_engineer_title():
    content = str(resolve_home_content("en").content)

    assert "AI Engineer" not in content
    assert "Robotics Engineer" not in content


def test_each_language_has_an_independent_content_module():
    assert resolve_home_content("id").content == HOME_ID
    assert resolve_home_content("en").content == HOME_EN
    assert resolve_home_content("ja").content == HOME_JA


def test_each_language_uses_the_same_content_schema():
    assert HOME_ID.keys() == HOME_EN.keys() == HOME_JA.keys()
    assert HOME_ID["ui"].keys() == HOME_EN["ui"].keys() == HOME_JA["ui"].keys()
