"""Cinematic title opening screen and main menu."""

from collections.abc import Callable

from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText
from panda3d.core import NodePath, TextNode, Vec4

from panda_motors.ui.theme_manager import ThemeManager


class MainMenuScreen:
    """Opening luxury showcase menu with cinematic backdrop."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        on_enter_showroom: Callable[[], None],
        on_open_catalog: Callable[[], None],
        on_open_configurator: Callable[[], None],
        on_start_tour: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_exit_app: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("main_menu_root")
        self.theme_manager = theme_manager

        self.on_enter_showroom = on_enter_showroom
        self.on_open_catalog = on_open_catalog
        self.on_open_configurator = on_open_configurator
        self.on_start_tour = on_start_tour
        self.on_open_settings = on_open_settings
        self.on_exit_app = on_exit_app

        self._build_menu()

    def _build_menu(self) -> None:
        theme = self.theme_manager.current

        # Glass panel container on left side for clear view of 3D showroom
        self.panel = DirectFrame(
            parent=self.root,
            frameColor=Vec4(0.05, 0.07, 0.10, 0.88),
            frameSize=(-0.45, 0.45, -0.75, 0.75),
            pos=(-0.85, 0, 0.0),
        )

        # Panda Motors Logo Title
        OnscreenText(
            text="P A N D A   M O T O R S",
            parent=self.panel,
            pos=(0, 0.58),
            scale=0.048,
            fg=theme.text_primary,
            align=TextNode.ACenter,
            mayChange=False,
        )

        OnscreenText(
            text="Drive  Your  Dreams",
            parent=self.panel,
            pos=(0, 0.51),
            scale=0.026,
            fg=theme.accent_primary,
            align=TextNode.ACenter,
            mayChange=False,
        )

        OnscreenText(
            text="FLAGSHIP LUXURY 3D SHOWROOM",
            parent=self.panel,
            pos=(0, 0.43),
            scale=0.022,
            fg=theme.text_dim,
            align=TextNode.ACenter,
            mayChange=False,
        )

        # Menu Action Buttons
        menu_items = [
            ("Enter Showroom", self.on_enter_showroom, True),
            ("Explore Vehicle Collection", self.on_open_catalog, False),
            ("Vehicle Configurator Studio", self.on_open_configurator, False),
            ("Guided Cinematic Tour", self.on_start_tour, False),
            ("Settings & Graphics", self.on_open_settings, False),
            ("Exit Application", self.on_exit_app, False),
        ]

        start_z = 0.28
        spacing = 0.115
        for i, (label, callback, is_primary) in enumerate(menu_items):
            DirectButton(
                parent=self.panel,
                text=label,
                text_scale=0.032,
                text_fg=Vec4(1, 1, 1, 1) if is_primary else theme.text_primary,
                text_pos=(0, -0.01),
                frameColor=theme.accent_primary if is_primary else theme.bg_card,
                frameSize=(-0.36, 0.36, -0.04, 0.048),
                pos=(0, 0, start_z - i * spacing),
                relief=None,
                command=callback,
            )

        # Tagline bottom
        OnscreenText(
            text="Explore  *  Discover  *  Drive",
            parent=self.panel,
            pos=(0, -0.66),
            scale=0.026,
            fg=theme.text_dim,
            align=TextNode.ACenter,
            mayChange=False,
        )

    def show(self) -> None:
        self.root.show()

    def hide(self) -> None:
        self.root.hide()
