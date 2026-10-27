"""Full-screen vehicle catalog browser with search, sorting, filtering, and comparison."""

from collections.abc import Callable

from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText
from panda3d.core import NodePath, TextNode, Vec4

from panda_motors.ui.theme_manager import ThemeManager
from panda_motors.vehicles.vehicle_catalog import VehicleCatalog


class VehicleBrowserScreen:
    """Full-screen luxury vehicle collection browser."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        catalog: VehicleCatalog,
        on_select_vehicle: Callable[[str], None],
        on_close: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("vehicle_browser_root")
        self.theme_manager = theme_manager
        self.catalog = catalog
        self.on_select_vehicle = on_select_vehicle
        self.on_close = on_close

        self.current_category = "All"
        self.current_sort = "power"
        self.search_query = ""
        self.compare_ids: list[str] = []
        self.showing_comparison: bool = False

        self._card_buttons: list[DirectFrame] = []
        self._build_screen()
        self.root.hide()

    def _build_screen(self) -> None:
        theme = self.theme_manager.current

        # Full screen darkened backdrop
        self.backdrop = DirectFrame(
            parent=self.root,
            frameColor=Vec4(0.04, 0.05, 0.08, 0.95),
            frameSize=(-1.65, 1.65, -1.0, 1.0),
            pos=(0, 0, 0),
        )

        # Header Title
        OnscreenText(
            text="PANDA MOTORS  —  VEHICLE COLLECTION",
            parent=self.backdrop,
            pos=(0, 0.82),
            scale=0.048,
            fg=theme.text_primary,
            align=TextNode.ACenter,
            mayChange=False,
        )

        # Category Filters Bar (Z = 0.70)
        categories = ["All", "Supercars", "Hypercars", "Sports coupes", "SUVs", "Luxury sedans", "Electric"]
        self.cat_btns: dict[str, DirectButton] = {}
        cat_start_x = -1.15
        cat_spacing = 0.38
        for i, cname in enumerate(categories):
            btn = DirectButton(
                parent=self.backdrop,
                text=cname,
                text_scale=0.028,
                text_fg=theme.text_primary if i == 0 else theme.text_secondary,
                text_pos=(0, -0.01),
                frameColor=theme.accent_primary if i == 0 else theme.bg_card,
                frameSize=(-0.17, 0.17, -0.03, 0.035),
                pos=(cat_start_x + i * cat_spacing, 0, 0.70),
                relief=None,
                command=self._filter_by_category,
                extraArgs=[cname],
            )
            self.cat_btns[cname] = btn

        # Sorting bar (Z = 0.60)
        OnscreenText(
            text="Sort By:",
            parent=self.backdrop,
            pos=(-1.15, 0.59),
            scale=0.026,
            fg=theme.text_dim,
            align=TextNode.ALeft,
            mayChange=False,
        )
        sort_options = [("Power (HP)", "power"), ("Acceleration", "accel"), ("Top Speed", "top_speed"), ("Price", "price")]
        for i, (slabel, scrit) in enumerate(sort_options):
            DirectButton(
                parent=self.backdrop,
                text=slabel,
                text_scale=0.026,
                text_fg=theme.text_primary,
                text_pos=(0, -0.008),
                frameColor=theme.bg_card,
                frameSize=(-0.12, 0.12, -0.026, 0.030),
                pos=(-0.85 + i * 0.28, 0, 0.60),
                relief=None,
                command=self._sort_catalog,
                extraArgs=[scrit],
            )

        # Compare Toggle Button
        self.btn_compare = DirectButton(
            parent=self.backdrop,
            text="Compare (0/3)",
            text_scale=0.026,
            text_fg=theme.text_primary,
            text_pos=(0, -0.008),
            frameColor=theme.bg_card,
            frameSize=(-0.12, 0.12, -0.026, 0.030),
            pos=(0.85, 0, 0.60),
            relief=None,
            command=self._toggle_comparison_view,
        )

        # Close / Return Button
        DirectButton(
            parent=self.backdrop,
            text="Close Catalog [Esc]",
            text_scale=0.032,
            text_fg=Vec4(1, 1, 1, 1),
            text_pos=(0, -0.01),
            frameColor=theme.accent_primary,
            frameSize=(-0.16, 0.16, -0.035, 0.04),
            pos=(1.35, 0, 0.82),
            relief=None,
            command=self.on_close,
        )

        # Cards Container Frame (Z = -0.15)
        self.cards_container = DirectFrame(
            parent=self.backdrop,
            frameColor=Vec4(0, 0, 0, 0),
            frameSize=(-1.4, 1.4, -0.65, 0.65),
            pos=(0, 0, -0.08),
        )

    def _filter_by_category(self, category: str) -> None:
        self.current_category = category
        theme = self.theme_manager.current
        for cname, btn in self.cat_btns.items():
            if cname == category:
                btn["frameColor"] = theme.accent_primary
                btn["text_fg"] = theme.text_primary
            else:
                btn["frameColor"] = theme.bg_card
                btn["text_fg"] = theme.text_secondary
        self._refresh_cards()

    def _sort_catalog(self, criterion: str) -> None:
        self.current_sort = criterion
        self._refresh_cards()

    def _refresh_cards(self) -> None:
        """Renders grid of vehicle cards matching current filter and sort."""
        for c in self._card_buttons:
            c.destroy()
        self._card_buttons.clear()

        vehicles = self.catalog.get_by_category(self.current_category)
        vehicles = self.catalog.sort_by(vehicles, self.current_sort)

        theme = self.theme_manager.current

        # Display up to 6 vehicles in a 3x2 grid
        col_x = [-0.95, 0.0, 0.95]
        row_z = [0.32, -0.28]

        for i, v in enumerate(vehicles[:6]):
            cx = col_x[i % 3]
            cz = row_z[i // 3]

            card = DirectFrame(
                parent=self.cards_container,
                frameColor=theme.bg_card,
                frameSize=(-0.42, 0.42, -0.26, 0.26),
                pos=(cx, 0, cz),
            )
            self._card_buttons.append(card)

            # Title
            OnscreenText(
                text=v.display_name,
                parent=card,
                pos=(-0.38, 0.18),
                scale=0.034,
                fg=theme.text_primary,
                align=TextNode.ALeft,
                mayChange=False,
            )
            # Category & Year
            OnscreenText(
                text=f"{v.category} * {v.year}",
                parent=card,
                pos=(-0.38, 0.13),
                scale=0.024,
                fg=theme.accent_primary,
                align=TextNode.ALeft,
                mayChange=False,
            )
            # Price
            OnscreenText(
                text=f"${v.price_usd:,} MSRP",
                parent=card,
                pos=(0.38, 0.18),
                scale=0.030,
                fg=Vec4(0.2, 0.85, 0.4, 1.0),
                align=TextNode.ARight,
                mayChange=False,
            )

            # Specs summary line
            specs = v.specifications
            spec_str = f"{specs.power_hp} HP   |   0-100: {specs.accel_0_100}s   |   Top: {specs.top_speed_kmh} km/h"
            OnscreenText(
                text=spec_str,
                parent=card,
                pos=(-0.38, 0.04),
                scale=0.024,
                fg=theme.text_secondary,
                align=TextNode.ALeft,
                mayChange=False,
            )

            # Short description
            desc_short = v.short_description[:75] + "..." if len(v.short_description) > 75 else v.short_description
            OnscreenText(
                text=desc_short,
                parent=card,
                pos=(-0.38, -0.04),
                scale=0.022,
                fg=theme.text_dim,
                align=TextNode.ALeft,
                mayChange=False,
            )

            # "Inspect in Showroom" button
            DirectButton(
                parent=card,
                text="Inspect in Showroom",
                text_scale=0.026,
                text_fg=Vec4(1, 1, 1, 1),
                text_pos=(0, -0.008),
                frameColor=theme.accent_primary,
                frameSize=(-0.16, 0.16, -0.028, 0.032),
                pos=(0.20, 0, -0.18),
                relief=None,
                command=self._on_inspect_clicked,
                extraArgs=[v.id],
            )

            # Add to Compare checkbox button
            in_cmp = v.id in self.compare_ids
            DirectButton(
                parent=card,
                text="[X] Compare" if in_cmp else "[+] Compare",
                text_scale=0.024,
                text_fg=theme.accent_primary if in_cmp else theme.text_dim,
                text_pos=(0, -0.008),
                frameColor=theme.bg_panel,
                frameSize=(-0.12, 0.12, -0.028, 0.032),
                pos=(-0.24, 0, -0.18),
                relief=None,
                command=self._toggle_compare_id,
                extraArgs=[v.id],
            )

    def _toggle_compare_id(self, vehicle_id: str) -> None:
        if vehicle_id in self.compare_ids:
            self.compare_ids.remove(vehicle_id)
        else:
            if len(self.compare_ids) < 3:
                self.compare_ids.append(vehicle_id)
        self.btn_compare["text"] = f"Compare ({len(self.compare_ids)}/3)"
        self._refresh_cards()

    def _toggle_comparison_view(self) -> None:
        if len(self.compare_ids) >= 2:
            self._render_comparison()

    def _render_comparison(self) -> None:
        """Displays side-by-side comparison modal of selected cars."""
        for c in self._card_buttons:
            c.destroy()
        self._card_buttons.clear()

        theme = self.theme_manager.current
        selected = self.catalog.compare_vehicles(self.compare_ids)

        comp_frame = DirectFrame(
            parent=self.cards_container,
            frameColor=theme.bg_panel,
            frameSize=(-1.3, 1.3, -0.55, 0.55),
            pos=(0, 0, 0),
        )
        self._card_buttons.append(comp_frame)

        OnscreenText(
            text="SIDE-BY-SIDE VEHICLE COMPARISON",
            parent=comp_frame,
            pos=(0, 0.44),
            scale=0.036,
            fg=theme.accent_primary,
            align=TextNode.ACenter,
        )

        metrics = ["Power", "0-100 km/h", "Top Speed", "Torque", "Weight", "Price"]
        for j, m in enumerate(metrics):
            mz = 0.30 - j * 0.10
            OnscreenText(text=m, parent=comp_frame, pos=(-1.15, mz), scale=0.026, fg=theme.text_dim, align=TextNode.ALeft)

        spacing = 0.70
        start_x = -0.40 if len(selected) == 2 else -0.70
        for i, veh in enumerate(selected):
            vx = start_x + i * spacing
            OnscreenText(text=veh.display_name, parent=comp_frame, pos=(vx, 0.38), scale=0.030, fg=theme.text_primary, align=TextNode.ACenter)

            s = veh.specifications
            vals = [
                f"{s.power_hp} HP",
                f"{s.accel_0_100} s",
                f"{s.top_speed_kmh} km/h",
                f"{s.torque_nm} Nm",
                f"{s.weight_kg} kg",
                f"${veh.price_usd:,}",
            ]
            for j, val in enumerate(vals):
                mz = 0.30 - j * 0.10
                OnscreenText(text=val, parent=comp_frame, pos=(vx, mz), scale=0.028, fg=theme.text_primary, align=TextNode.ACenter)

        # Back to grid button
        DirectButton(
            parent=comp_frame,
            text="< Back to Catalog",
            text_scale=0.028,
            text_fg=Vec4(1, 1, 1, 1),
            text_pos=(0, -0.01),
            frameColor=theme.accent_primary,
            frameSize=(-0.16, 0.16, -0.03, 0.035),
            pos=(0, 0, -0.45),
            relief=None,
            command=self._refresh_cards,
        )

    def _on_inspect_clicked(self, vehicle_id: str) -> None:
        self.hide()
        self.on_select_vehicle(vehicle_id)

    def show(self) -> None:
        self._refresh_cards()
        self.root.show()

    def hide(self) -> None:
        self.root.hide()
