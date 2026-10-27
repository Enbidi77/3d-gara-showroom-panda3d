"""Heads-Up Display (HUD) overlay matching luxury automotive design language."""

from collections.abc import Callable

from direct.gui.DirectGui import (
    DirectButton,
    DirectFrame,
    OnscreenText,
)
from panda3d.core import (
    NodePath,
    TextNode,
    Vec4,
)

from panda_motors.core.events import EventBus
from panda_motors.core.performance import PerformanceMonitor
from panda_motors.ui.theme_manager import ThemeManager


class HUD:
    """Showroom exploration Heads-Up Display."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        perf_monitor: PerformanceMonitor,
        on_nav_tab_click: Callable[[str], None],
        on_category_click: Callable[[str], None],
        on_view_preset_click: Callable[[str], None],
        on_settings_click: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("hud_root")
        self.theme_manager = theme_manager
        self.perf_monitor = perf_monitor

        self.on_nav_tab_click = on_nav_tab_click
        self.on_category_click = on_category_click
        self.on_view_preset_click = on_view_preset_click
        self.on_settings_click = on_settings_click

        self.visible: bool = True
        self.event_bus = EventBus.get_instance()

        self._build_top_bar()
        self._build_category_sidebar()
        self._build_controls_card()
        self._build_zone_badge()
        self._build_tagline()
        self._build_view_presets()
        self._build_interaction_prompt()
        self._build_fps_counter()

    def _build_top_bar(self) -> None:
        """Constructs top glass bar with logo, nav tabs, and user profile."""
        theme = self.theme_manager.current
        # Top translucent bar frame across top of screen
        self.top_bar = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-1.65, 1.65, -0.07, 0.07),
            pos=(0, 0, 0.91),
        )

        # Panda Motors Logo (Panda Face + Text)
        OnscreenText(
            text="Panda Motors",
            parent=self.top_bar,
            pos=(-1.45, -0.018),
            scale=0.048,
            fg=theme.text_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        # Main Nav Tabs: Home, Showroom, Collection, About
        nav_tabs = [
            ("Home", -0.45),
            ("Showroom", -0.22),
            ("Collection", 0.05),
            ("Tour", 0.30),
        ]

        self.nav_buttons: dict[str, DirectButton] = {}
        for name, x in nav_tabs:
            is_active = (name == "Showroom")
            btn = DirectButton(
                parent=self.top_bar,
                text=name,
                text_scale=0.038,
                text_fg=theme.text_primary if is_active else theme.text_secondary,
                text_pos=(0, -0.012),
                frameColor=theme.accent_primary if is_active else Vec4(0, 0, 0, 0),
                frameSize=(-0.11, 0.11, -0.035, 0.045),
                pos=(x, 0, 0),
                relief=None,
                command=self.on_nav_tab_click,
                extraArgs=[name],
            )
            self.nav_buttons[name] = btn

        # Right side: Settings & Fullscreen
        self.btn_settings = DirectButton(
            parent=self.top_bar,
            text="Settings",
            text_scale=0.034,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.09, 0.09, -0.03, 0.038),
            pos=(1.45, 0, 0),
            relief=None,
            command=self.on_settings_click,
        )

    def _build_category_sidebar(self) -> None:
        """Constructs left vehicle filter pill sidebar."""
        theme = self.theme_manager.current
        # Left translucent glass panel
        self.sidebar_frame = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-0.16, 0.16, -0.32, 0.32),
            pos=(-1.42, 0, 0.40),
        )

        categories = [
            "All Cars",
            "Supercars",
            "Hypercars",
            "Sports coupes",
            "SUVs",
            "Luxury sedans",
            "Electric",
        ]

        self.category_buttons: dict[str, DirectButton] = {}
        start_z = 0.23
        for i, cat in enumerate(categories):
            is_active = (i == 0)
            btn = DirectButton(
                parent=self.sidebar_frame,
                text=cat,
                text_scale=0.032,
                text_fg=theme.text_primary if is_active else theme.text_secondary,
                text_pos=(0, -0.01),
                frameColor=theme.accent_primary if is_active else Vec4(0, 0, 0, 0),
                frameSize=(-0.14, 0.14, -0.03, 0.038),
                pos=(0, 0, start_z - i * 0.082),
                relief=None,
                command=self._on_cat_selected,
                extraArgs=[cat],
            )
            self.category_buttons[cat] = btn

    def _on_cat_selected(self, cat: str) -> None:
        theme = self.theme_manager.current
        for name, btn in self.category_buttons.items():
            if name == cat:
                btn["frameColor"] = theme.accent_primary
                btn["text_fg"] = theme.text_primary
            else:
                btn["frameColor"] = Vec4(0, 0, 0, 0)
                btn["text_fg"] = theme.text_secondary
        self.on_category_click(cat)

    def _build_controls_card(self) -> None:
        """Constructs bottom-right keyboard/mouse control hints card."""
        theme = self.theme_manager.current
        self.controls_frame = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-0.25, 0.25, -0.18, 0.18),
            pos=(1.35, 0, -0.72),
        )

        hints = [
            ("W A S D", "Move"),
            ("Mouse", "Look around"),
            ("E", "Interact / Inspect"),
            ("F", "1st / 3rd Person"),
            ("Tab", "Showroom Menu"),
            ("Esc", "Settings"),
        ]

        for i, (key, desc) in enumerate(hints):
            z = 0.11 - i * 0.048
            OnscreenText(
                text=key,
                parent=self.controls_frame,
                pos=(-0.21, z),
                scale=0.028,
                fg=theme.accent_primary,
                align=TextNode.ALeft,
                mayChange=False,
            )
            OnscreenText(
                text=desc,
                parent=self.controls_frame,
                pos=(-0.04, z),
                scale=0.028,
                fg=theme.text_secondary,
                align=TextNode.ALeft,
                mayChange=False,
            )

    def _build_zone_badge(self) -> None:
        """Constructs bottom-left zone badge next to minimap."""
        theme = self.theme_manager.current
        self.zone_frame = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-0.24, 0.24, -0.06, 0.06),
            pos=(-0.85, 0, -0.70),
        )

        self.txt_zone_title = OnscreenText(
            text="Main Showroom",
            parent=self.zone_frame,
            pos=(-0.20, 0.01),
            scale=0.038,
            fg=theme.text_primary,
            align=TextNode.ALeft,
            mayChange=True,
        )
        self.txt_zone_desc = OnscreenText(
            text="Explore flagship collection",
            parent=self.zone_frame,
            pos=(-0.20, -0.035),
            scale=0.026,
            fg=theme.text_secondary,
            align=TextNode.ALeft,
            mayChange=True,
        )

    def set_zone_info(self, title: str, subtitle: str) -> None:
        self.txt_zone_title.setText(title)
        self.txt_zone_desc.setText(subtitle)

    def _build_tagline(self) -> None:
        """Constructs brand tagline in bottom-left corner."""
        theme = self.theme_manager.current
        OnscreenText(
            text="Explore  *  Discover  *  Drive",
            parent=self.root,
            pos=(-1.45, -0.93),
            scale=0.035,
            fg=theme.text_dim,
            align=TextNode.ALeft,
            mayChange=False,
        )

    def _build_view_presets(self) -> None:
        """Constructs right-hand stack of camera viewpoint shortcuts."""
        theme = self.theme_manager.current
        self.presets_frame = DirectFrame(
            parent=self.root,
            frameColor=Vec4(0, 0, 0, 0),
            frameSize=(-0.08, 0.08, -0.28, 0.28),
            pos=(1.52, 0, 0.05),
        )

        views = [
            ("Overview", "main_showroom"),
            ("Hypercar", "hypercar_exhibition"),
            ("Supercar", "supercar_gallery"),
            ("Lounge", "customer_lounge"),
        ]

        for i, (label, zone_id) in enumerate(views):
            z = 0.18 - i * 0.11
            DirectButton(
                parent=self.presets_frame,
                text=label,
                text_scale=0.030,
                text_fg=theme.text_primary,
                text_pos=(0, -0.01),
                frameColor=theme.bg_panel,
                frameSize=(-0.075, 0.075, -0.04, 0.045),
                pos=(0, 0, z),
                relief=None,
                command=self.on_view_preset_click,
                extraArgs=[zone_id],
            )

    def _build_interaction_prompt(self) -> None:
        """Floating interaction prompt when close to a vehicle."""
        theme = self.theme_manager.current
        self.prompt_frame = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-0.30, 0.30, -0.05, 0.05),
            pos=(0, 0, -0.35),
        )
        self.prompt_text = OnscreenText(
            text="Press [E] to Inspect Vehicle",
            parent=self.prompt_frame,
            pos=(0, -0.015),
            scale=0.038,
            fg=theme.accent_primary,
            align=TextNode.ACenter,
            mayChange=True,
        )
        self.prompt_frame.hide()

    def show_interaction_prompt(self, vehicle_name: str) -> None:
        self.prompt_text.setText(f"Press [E] to Inspect  {vehicle_name}")
        self.prompt_frame.show()

    def hide_interaction_prompt(self) -> None:
        self.prompt_frame.hide()

    def _build_fps_counter(self) -> None:
        """Top-left FPS and frame time monitor."""
        self.fps_text = OnscreenText(
            text="FPS: 60.0",
            parent=self.root,
            pos=(-1.58, 0.81),
            scale=0.026,
            fg=Vec4(0.4, 0.9, 0.4, 0.9),
            align=TextNode.ALeft,
            mayChange=True,
        )

    def update(self) -> None:
        """Updates live performance metrics each frame."""
        if self.visible:
            fps = self.perf_monitor.fps
            ms = self.perf_monitor.frame_time_ms
            self.fps_text.setText(f"FPS: {fps:.1f} ({ms:.1f}ms)")

    def toggle_visibility(self) -> bool:
        self.visible = not self.visible
        if self.visible:
            self.root.show()
        else:
            self.root.hide()
        return self.visible
