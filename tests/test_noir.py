import pytest

from beaverhabits.frontend import icons, noir


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", 16),
        ("18", 18),
        (" 17 ", 17),
        ("abc", 16),
        ("11", 12),
        ("40", 22),
        ("16.5", 16),
    ],
)
def test_parse_font_size_defaults_and_clamps(raw, expected):
    assert noir.parse_font_size(raw) == expected


def test_palette_colors_work_with_icon_fade():
    for color in (noir.ACCENT, noir.ON_ACCENT, noir.CELL, noir.TEXT_MUTED, noir.FAINT):
        assert icons.fade(color, 0.5).startswith("rgba(")


def test_css_uses_font_size_and_scopes_colors_to_dark():
    css = noir.noir_css(18)
    assert "font-size: 18px" in css
    assert ".body--dark" in css
    assert "#F5A623" in css
    assert "#0B0B0C" in css


def test_accent_follows_dark_mode(monkeypatch):
    monkeypatch.setattr(noir, "ENABLED", True)
    assert noir.accent(default="rgb(1,2,3)") == noir.ACCENT
    monkeypatch.setattr(noir, "ENABLED", False)
    assert noir.accent(default="rgb(1,2,3)") == "rgb(1,2,3)"
