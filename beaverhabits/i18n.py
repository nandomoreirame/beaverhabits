"""Minimal i18n for the fork.

The English source text is the lookup key (gettext style), so a missing
translation falls back to English. The language comes from the LANGUAGE
environment variable (for example LANGUAGE=pt-BR) and defaults to English.
"""

import datetime
import json
import os
from functools import cache
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"

SUPPORTED = {"en": "en", "pt-br": "pt-BR"}
LOCALE_FILES = {"pt-BR": "pt_BR.json"}
QUASAR_LANGUAGES = {"en": "en-US", "pt-BR": "pt-BR"}

DAY_ABBR = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "pt-BR": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
}
MONTH_ABBR = {
    "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
    "pt-BR": "jan fev mar abr mai jun jul ago set out nov dez".split(),
}
MONTH_NAME = {
    "en": (
        "January February March April May June July August September October "
        "November December"
    ).split(),
    "pt-BR": (
        "janeiro fevereiro março abril maio junho julho agosto setembro outubro "
        "novembro dezembro"
    ).split(),
}


def normalize_language(value: str) -> str:
    """Map LANGUAGE values such as 'pt_BR', 'PT-br' or 'pt_BR:pt' to a supported code."""
    first = (value or "").split(":")[0].strip().replace("_", "-").lower()
    return SUPPORTED.get(first, "en")


LANGUAGE = normalize_language(os.environ.get("LANGUAGE", ""))


@cache
def _catalog(language: str) -> dict[str, str]:
    filename = LOCALE_FILES.get(language)
    if not filename:
        return {}
    return json.loads((LOCALES_DIR / filename).read_text("utf-8"))


def t(text: str, **kwargs) -> str:
    """Translate an English source text, then fill its {placeholders}."""
    translated = _catalog(LANGUAGE).get(text, text)
    return translated.format(**kwargs) if kwargs else translated


def quasar_language() -> str:
    return QUASAR_LANGUAGES[LANGUAGE]


def day_abbr(weekday: int) -> str:
    """Abbreviated weekday name; 0 is Monday, like datetime.weekday()."""
    return DAY_ABBR[LANGUAGE][weekday % 7]


def month_abbr(month: int) -> str:
    return MONTH_ABBR[LANGUAGE][month - 1]


def long_date(day: datetime.date) -> str:
    month = MONTH_NAME[LANGUAGE][day.month - 1]
    if LANGUAGE == "pt-BR":
        return f"{day.day} de {month} de {day.year}"
    return f"{month} {day.day:02d}, {day.year}"  # same as strftime("%B %d, %Y")
