"""Self-hosted typography for the fork: Inter for text, JetBrains Mono for numbers.

Font files live in statics/fonts (SIL Open Font License, see LICENSE-fonts.txt).
"""

from nicegui import ui

LATIN = (
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, "
    "U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, "
    "U+2212, U+2215, U+FEFF, U+FFFD"
)
LATIN_EXT = (
    "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, "
    "U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, "
    "U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF"
)

TEXT_FONT = "'Inter Variable', system-ui, -apple-system, 'Segoe UI', sans-serif"
NUMERIC_FONT = "'JetBrains Mono Variable', ui-monospace, monospace"


def _font_face(family: str, slug: str) -> str:
    faces = []
    for subset, unicode_range in (("latin-ext", LATIN_EXT), ("latin", LATIN)):
        faces.append(f"""@font-face {{
  font-family: '{family}';
  font-style: normal;
  font-display: swap;
  font-weight: 100 900;
  src: url(/statics/fonts/{slug}-{subset}-wght-normal.woff2) format('woff2-variations');
  unicode-range: {unicode_range};
}}""")
    return "\n".join(faces)


FONTS_CSS = f"""
{_font_face("Inter Variable", "inter")}
{_font_face("JetBrains Mono Variable", "jetbrains-mono")}

body, .q-btn, .q-field, .q-item, .q-menu, .q-dialog, input, textarea {{
  font-family: {TEXT_FONT};
  font-feature-settings: 'cv11', 'ss01';
}}

.theme-header-date, .theme-numeric, .q-date__calendar-days, .q-date__calendar-item {{
  font-family: {NUMERIC_FONT};
  font-variant-numeric: tabular-nums;
}}
"""


def apply_fonts() -> None:
    ui.add_css(FONTS_CSS)
