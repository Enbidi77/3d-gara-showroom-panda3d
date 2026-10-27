"""Theme manager for dark and light luxury glass aesthetics."""

from dataclasses import dataclass

from panda3d.core import Vec4


@dataclass
class UITheme:
    name: str
    bg_panel: Vec4
    bg_card: Vec4
    bg_card_hover: Vec4
    accent_primary: Vec4
    accent_hover: Vec4
    text_primary: Vec4
    text_secondary: Vec4
    text_dim: Vec4
    border_subtle: Vec4
    border_highlight: Vec4


THEMES: dict[str, UITheme] = {
    "dark": UITheme(
        name="Dark Luxury",
        bg_panel=Vec4(0.06, 0.08, 0.12, 0.88),
        bg_card=Vec4(0.10, 0.12, 0.16, 0.82),
        bg_card_hover=Vec4(0.16, 0.20, 0.28, 0.95),
        accent_primary=Vec4(0.15, 0.60, 0.98, 1.0),
        accent_hover=Vec4(0.30, 0.75, 1.0, 1.0),
        text_primary=Vec4(0.96, 0.97, 0.99, 1.0),
        text_secondary=Vec4(0.68, 0.72, 0.80, 1.0),
        text_dim=Vec4(0.45, 0.48, 0.55, 1.0),
        border_subtle=Vec4(0.22, 0.26, 0.34, 0.65),
        border_highlight=Vec4(0.35, 0.65, 0.95, 0.8),
    ),
    "light": UITheme(
        name="Bright Gallery",
        bg_panel=Vec4(0.94, 0.95, 0.97, 0.92),
        bg_card=Vec4(0.98, 0.98, 1.0, 0.90),
        bg_card_hover=Vec4(0.88, 0.92, 0.96, 0.95),
        accent_primary=Vec4(0.08, 0.48, 0.88, 1.0),
        accent_hover=Vec4(0.18, 0.58, 0.98, 1.0),
        text_primary=Vec4(0.10, 0.12, 0.15, 1.0),
        text_secondary=Vec4(0.38, 0.42, 0.48, 1.0),
        text_dim=Vec4(0.55, 0.58, 0.62, 1.0),
        border_subtle=Vec4(0.78, 0.80, 0.85, 0.75),
        border_highlight=Vec4(0.20, 0.55, 0.85, 0.85),
    ),
}


class ThemeManager:
    """Provides active color schemes and manages runtime theme switching."""

    def __init__(self, default_theme: str = "dark") -> None:
        self.current_theme_name = default_theme
        self.current = THEMES.get(default_theme, THEMES["dark"])

    def set_theme(self, theme_name: str) -> None:
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current = THEMES[theme_name]

    def toggle_theme(self) -> str:
        new_name = "light" if self.current_theme_name == "dark" else "dark"
        self.set_theme(new_name)
        return new_name
