import datetime
import json

import pytest

from beaverhabits import i18n

DAY = datetime.date(2026, 11, 21)  # Saturday


@pytest.fixture
def pt(monkeypatch):
    monkeypatch.setattr(i18n, "LANGUAGE", "pt-BR")


@pytest.fixture
def en(monkeypatch):
    monkeypatch.setattr(i18n, "LANGUAGE", "en")


def test_english_returns_source_text(en):
    assert i18n.t("Save") == "Save"


def test_portuguese_translates_known_text(pt):
    assert i18n.t("Save") == "Salvar"


def test_unknown_text_falls_back_to_source(pt):
    assert i18n.t("Some text nobody translated") == "Some text nobody translated"


def test_placeholders_are_formatted_after_translation(pt):
    assert i18n.t("{days} days ago", days=3) == "há 3 dias"


def test_placeholders_in_english(en):
    assert i18n.t("{days} days ago", days=3) == "3 days ago"


def test_normalize_language_accepts_variants():
    assert i18n.normalize_language("pt_BR") == "pt-BR"
    assert i18n.normalize_language("PT-br") == "pt-BR"
    assert i18n.normalize_language("") == "en"
    assert i18n.normalize_language("xx") == "en"


def test_quasar_language(pt):
    assert i18n.quasar_language() == "pt-BR"


def test_quasar_language_default(en):
    assert i18n.quasar_language() == "en-US"


def test_day_abbr_portuguese(pt):
    assert [i18n.day_abbr(n) for n in range(7)] == [
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sáb",
        "Dom",
    ]


def test_day_abbr_english(en):
    assert i18n.day_abbr(5) == "Sat"


def test_month_abbr(pt):
    assert i18n.month_abbr(2) == "fev"


def test_month_abbr_english(en):
    assert i18n.month_abbr(2) == "Feb"


def test_long_date_portuguese(pt):
    assert i18n.long_date(DAY) == "21 de novembro de 2026"


def test_long_date_english(en):
    assert i18n.long_date(DAY) == "November 21, 2026"


def test_every_portuguese_entry_is_filled_and_keeps_placeholders():
    data = json.loads(i18n.LOCALES_DIR.joinpath("pt_BR.json").read_text("utf-8"))
    assert data
    for source, target in data.items():
        assert target.strip(), source
        assert sorted(_placeholders(source)) == sorted(_placeholders(target)), source


def _placeholders(text: str) -> list[str]:
    import string

    return [f for _, f, _, _ in string.Formatter().parse(text) if f]
