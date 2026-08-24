from django.conf import settings
from django.utils import translation


def test_supported_locales_and_default_timezone():
    language_codes = {code for code, _name in settings.LANGUAGES}

    assert language_codes == {"uz", "ru", "en"}
    assert settings.LANGUAGE_CODE == "uz"
    assert settings.TIME_ZONE == "Asia/Tashkent"


def test_locale_can_be_activated():
    with translation.override("ru"):
        assert translation.get_language() == "ru"
