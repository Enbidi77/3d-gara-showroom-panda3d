"""Showroom zone fast-travel and teleportation destination menu."""

from collections.abc import Callable

from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText
from panda3d.core import NodePath, TextNode, Vec4

from panda_motors.ui.theme_manager import ThemeManager
from panda_motors.world.showroom_zones import ShowroomZoneRegistry


class NavigationMenuModal:
    """Showroom destination directory allowing one-click teleportation to any zone."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        zone_registry: ShowroomZoneRegistry,
        on_select_zone: Callable[[str], None],
        on_start_tour: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("nav_modal_root")
        self.theme_manager = theme_manager
        self.zone_registry = zone_registry
        self.on_select_zone = on_select_zone
        self.on_start_tour = on_start_tour
        self.on_close = on_close

        self._build_menu()
        self.root.hide()

    def _build_menu(self) -> None:
        theme = self.theme_manager.current

        self.backdrop = DirectFrame(
            parent=self.root,
            frameColor=Vec4(0.05, 0.06, 0.09, 0.94),
            frameSize=(-1.35, 1.35, -0.85, 0.85),
            pos=(0, 0, 0),
        )

        OnscreenText(
            text="SHOWROOM DESTINATIONS & FAST TRAVEL",
            parent=self.backdrop,
            pos=(0, 0.72),
            scale=0.044,
            fg=theme.text_primary,
            align=TextNode.ACenter,
            mayChange=False,
        )
        OnscreenText(
            text="Select a destination to smoothly travel or launch an automated guided tour",
            parent=self.backdrop,
            pos=(0, 0.65),
            scale=0.026,
            fg=theme.text_secondary,
            align=TextNode.ACenter,
            mayChange=False,
        )

        # Guided Tour Quick Action
        DirectButton(
            parent=self.backdrop,
            text="Launch Guided Cinematic Tour",
            text_scale=0.030,
            text_fg=Vec4(1, 1, 1, 1),
            text_pos=(0, -0.01),
            frameColor=theme.accent_primary,
            frameSize=(-0.24, 0.24, -0.035, 0.04),
            pos=(0, 0, 0.54),
            relief=None,
            command=self._on_tour_clicked,
        )

        # Grid of 9 destinations (3 rows of 3)
        zones = self.zone_registry.get_all_zones()
        col_x = [-0.85, 0.0, 0.85]
        row_z = [0.32, -0.04, -0.40]

        for i, z in enumerate(zones[:9]):
            cx = col_x[i % 3]
            cz = row_z[i // 3]

            card = DirectFrame(
                parent=self.backdrop,
                frameColor=theme.bg_card,
                frameSize=(-0.38, 0.38, -0.14, 0.14),
                pos=(cx, 0, cz),
            )

            # Zone Name
            OnscreenText(
                text=z.name,
                parent=card,
                pos=(-0.34, 0.08),
                scale=0.030,
                fg=theme.accent_primary,
                align=TextNode.ALeft,
            )

            # Short description
            desc = z.description[:60] + "..." if len(z.description) > 60 else z.description
            OnscreenText(
                text=desc,
                parent=card,
                pos=(-0.34, 0.02),
                scale=0.020,
                fg=theme.text_secondary,
                align=TextNode.ALeft,
            )

            # Travel Button
            DirectButton(
                parent=card,
                text="Travel Here",
                text_scale=0.024,
                text_fg=Vec4(1, 1, 1, 1),
                text_pos=(0, -0.008),
                frameColor=theme.accent_primary,
                frameSize=(-0.11, 0.11, -0.025, 0.030),
                pos=(0.24, 0, -0.08),
                relief=None,
                command=self._on_zone_clicked,
                extraArgs=[z.id],
            )

        # Close Button
        DirectButton(
            parent=self.backdrop,
            text="Close [Tab / Esc]",
            text_scale=0.030,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.16, 0.16, -0.035, 0.04),
            pos=(0, 0, -0.72),
            relief=None,
            command=self.on_close,
        )

    def _on_zone_clicked(self, zone_id: str) -> None:
        self.hide()
        self.on_select_zone(zone_id)

    def _on_tour_clicked(self) -> None:
        self.hide()
        self.on_start_tour()

    def show(self) -> None:
        self.root.show()

    def hide(self) -> None:
        self.root.hide()

    def toggle(self) -> bool:
        if self.root.isHidden():
            self.show()
            return True
        else:
            self.hide()
            return False
