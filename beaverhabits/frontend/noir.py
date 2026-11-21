"""Terminal Noir theme for dark mode (fork addition).

Colors come from terminalnoir palette.json v0.3.2 (variant "dark").
CSS overrides apply only under .body--dark. SVG icons and heatmap cells
carry inline colors, so they switch to this palette when DARK_MODE=true.
FONT_SIZE (px, default 16) sets the base text size in every theme.
"""

import os

from nicegui import ui

from beaverhabits.configs import settings

# Palette as hex (CSS) and rgb() (icons.fade accepts only rgb()).
BASE_HEX = "#0B0B0C"
RAISED_HEX = "#121214"
ELEVATED_HEX = "#18181B"
BORDER_HEX = "#222226"
OUTLINE_HEX = "#64646B"
SELECTION_HEX = "#52525B"
TEXT_HEX = "#F4F4F5"
TEXT_MUTED_HEX = "#A1A1AA"
FAINT_HEX = "#6B6B74"
ACCENT_HEX = "#F5A623"
ON_ACCENT_HEX = "#0B0B0C"
ERROR_HEX = "#FFB7B0"

ACCENT = "rgb(245,166,35)"
ON_ACCENT = "rgb(11,11,12)"
CELL = "rgb(34,34,38)"  # surface.border: empty heatmap cell on a raised card
TEXT_MUTED = "rgb(161,161,170)"
FAINT = "rgb(107,107,116)"
PERIOD_DONE = "rgb(92,64,20)"  # accent at ~35% over the base surface

DEFAULT_FONT_SIZE = 16
MIN_FONT_SIZE, MAX_FONT_SIZE = 12, 22

ENABLED = settings.DARK_MODE is True


def parse_font_size(raw: str) -> int:
    """Read FONT_SIZE in px; invalid values fall back to the default, then clamp."""
    try:
        value = int((raw or "").strip())
    except ValueError:
        return DEFAULT_FONT_SIZE
    return max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, value))


FONT_SIZE = parse_font_size(os.environ.get("FONT_SIZE", ""))


def accent(default: str) -> str:
    return ACCENT if ENABLED else default


def pick(noir_value: str, default: str) -> str:
    return noir_value if ENABLED else default


def noir_css(font_size: int) -> str:
    return f"""
html, body {{
  font-size: {font_size}px;
}}
.theme-header-date {{
  font-size: {round(font_size * 0.8)}px !important;
}}

.body--dark {{
  --q-primary: {ACCENT_HEX} !important;
  --q-dark: {RAISED_HEX};
  --q-dark-page: {BASE_HEX};
  --q-negative: {ERROR_HEX};
  background-color: {BASE_HEX};
  color: {TEXT_HEX};
  caret-color: {ACCENT_HEX};
  scrollbar-color: {BORDER_HEX} {BASE_HEX};

  ::selection {{
    background: {SELECTION_HEX};
  }}

  .nicegui-link, .theme-menu-icon {{
    color: {TEXT_HEX};
  }}
  .theme-header-date {{
    color: {TEXT_MUTED_HEX};
  }}
  .theme-icon-checkbox .q-checkbox__inner--truthy .q-checkbox__icon {{
    color: {ACCENT_HEX};
  }}
  .theme-icon-checkbox .q-checkbox__inner--falsy .q-checkbox__icon {{
    color: {FAINT_HEX};
  }}
  .text-gray-300, .dark\\:text-gray-300 {{
    color: {TEXT_MUTED_HEX} !important;
  }}

  .q-card, .q-card--dark {{
    background: {RAISED_HEX};
    border: 1px solid {BORDER_HEX};
    border-radius: 8px;
    box-shadow: none;
  }}
  .q-menu, .q-menu--dark, .q-dialog .q-card {{
    background: {ELEVATED_HEX};
    border: 1px solid {BORDER_HEX};
    border-radius: 6px;
  }}
  .q-item.q-manual-focusable--focused, .q-item:hover {{
    background: rgba(245, 166, 35, 0.15);
    color: {ACCENT_HEX};
  }}
  .q-separator--dark {{
    background: {BORDER_HEX};
  }}

  .q-field--dark .q-field__control:before {{
    border-color: {OUTLINE_HEX};
  }}
  .q-field--dark .q-field__label, .q-field--dark .q-field__native::placeholder {{
    color: {TEXT_MUTED_HEX};
  }}

  .bg-primary, .q-btn.bg-primary {{
    color: {ON_ACCENT_HEX} !important;
  }}
  .q-date--dark {{
    background: transparent;
  }}
  .q-date__calendar-weekdays > div {{
    color: {FAINT_HEX};
  }}

  .q-timeline--dark .q-timeline__subtitle {{
    color: {TEXT_MUTED_HEX};
  }}
  .q-notification {{
    border-radius: 6px;
  }}
}}
"""


def apply_theme() -> None:
    ui.add_css(noir_css(FONT_SIZE))
