"""Vehicle inspection and specification detail overlay panel."""

from collections.abc import Callable

from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText
from panda3d.core import NodePath, TextNode, Vec4

from panda_motors.ui.theme_manager import ThemeManager
from panda_motors.vehicles.configurator import VehicleConfigurator
from panda_motors.vehicles.vehicle import Vehicle
from panda_motors.vehicles.vehicle_inspector import VehicleInspector


class VehicleDetailsPanel:
    """Detailed vehicle specification, orbit camera controls, and paint color selector."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        inspector: VehicleInspector,
        configurator: VehicleConfigurator,
        on_exit: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("vehicle_details_root")
        self.theme_manager = theme_manager
        self.inspector = inspector
        self.configurator = configurator
        self.on_exit = on_exit

        self.active_vehicle: Vehicle | None = None
        self._build_panel()
        self.root.hide()

    def _build_panel(self) -> None:
        theme = self.theme_manager.current

        # 1. Right-side vehicle specification card
        self.card = DirectFrame(
            parent=self.root,
            frameColor=theme.bg_panel,
            frameSize=(-0.38, 0.38, -0.72, 0.72),
            pos=(1.22, 0, 0.0),
        )

        # Title & Subtitle
        self.txt_title = OnscreenText(
            text="McLaren 750S",
            parent=self.card,
            pos=(-0.32, 0.62),
            scale=0.046,
            fg=theme.text_primary,
            align=TextNode.ALeft,
            mayChange=True,
        )
        self.txt_subtitle = OnscreenText(
            text="Panda Supercar Series * 2026",
            parent=self.card,
            pos=(-0.32, 0.56),
            scale=0.028,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=True,
        )

        # Price tag
        self.txt_price = OnscreenText(
            text="$329,500 MSRP",
            parent=self.card,
            pos=(-0.32, 0.49),
            scale=0.040,
            fg=Vec4(0.2, 0.85, 0.4, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
        )

        # Specifications Grid
        self.spec_labels: list[OnscreenText] = []
        spec_keys = [
            ("Engine", "4.0L Twin-Turbo V8"),
            ("Power", "740 HP"),
            ("Torque", "800 Nm"),
            ("0-100 km/h", "2.8 sec"),
            ("Top Speed", "332 km/h"),
            ("Drivetrain", "Rear-Wheel Drive"),
            ("Transmission", "7-Speed Dual-Clutch"),
        ]

        for i, (label, val) in enumerate(spec_keys):
            z = 0.40 - i * 0.058
            OnscreenText(
                text=label,
                parent=self.card,
                pos=(-0.32, z),
                scale=0.026,
                fg=theme.text_dim,
                align=TextNode.ALeft,
                mayChange=False,
            )
            txt_val = OnscreenText(
                text=val,
                parent=self.card,
                pos=(0.32, z),
                scale=0.028,
                fg=theme.text_primary,
                align=TextNode.ARight,
                mayChange=True,
            )
            self.spec_labels.append(txt_val)

        # Section: Exterior Paint Colors
        OnscreenText(
            text="EXTERIOR COLOR SELECTION",
            parent=self.card,
            pos=(-0.32, -0.06),
            scale=0.026,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        self.color_swatch_frame = DirectFrame(
            parent=self.card,
            frameColor=Vec4(0, 0, 0, 0),
            frameSize=(-0.35, 0.35, -0.08, 0.08),
            pos=(0, 0, -0.15),
        )
        self.swatch_buttons: list[DirectButton] = []

        # Section: Paint Finish (Metallic, Matte, Gloss)
        OnscreenText(
            text="PAINT FINISH",
            parent=self.card,
            pos=(-0.32, -0.26),
            scale=0.026,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        finishes = [("Metallic", -0.22), ("Matte", 0.0), ("Gloss", 0.22)]
        for fname, fx in finishes:
            DirectButton(
                parent=self.card,
                text=fname,
                text_scale=0.028,
                text_fg=theme.text_primary,
                text_pos=(0, -0.01),
                frameColor=theme.bg_card,
                frameSize=(-0.09, 0.09, -0.03, 0.035),
                pos=(fx, 0, -0.32),
                relief=None,
                command=self._set_finish,
                extraArgs=[fname.lower()],
            )

        # Camera Angles & Turntable Controls
        OnscreenText(
            text="INSPECTION CONTROLS",
            parent=self.card,
            pos=(-0.32, -0.40),
            scale=0.026,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        cam_angles = [
            ("Front", -0.24, "front"),
            ("Side", -0.08, "side"),
            ("Rear", 0.08, "rear"),
            ("Wheel", 0.24, "wheel"),
        ]
        for cname, cx, cpreset in cam_angles:
            DirectButton(
                parent=self.card,
                text=cname,
                text_scale=0.026,
                text_fg=theme.text_primary,
                text_pos=(0, -0.01),
                frameColor=theme.bg_card,
                frameSize=(-0.07, 0.07, -0.028, 0.032),
                pos=(cx, 0, -0.46),
                relief=None,
                command=self.inspector.set_viewpoint,
                extraArgs=[cpreset],
            )

        # Feature Toggles (Turntable, Lights)
        DirectButton(
            parent=self.card,
            text="Toggle Turntable",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.15, 0.15, -0.03, 0.035),
            pos=(-0.16, 0, -0.54),
            relief=None,
            command=self.inspector.toggle_turntable,
        )
        DirectButton(
            parent=self.card,
            text="Toggle Lights",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.15, 0.15, -0.03, 0.035),
            pos=(0.16, 0, -0.54),
            relief=None,
            command=self.inspector.toggle_headlights,
        )

        # Return to Showroom Button
        DirectButton(
            parent=self.card,
            text="< Return to Showroom",
            text_scale=0.034,
            text_fg=Vec4(1, 1, 1, 1),
            text_pos=(0, -0.012),
            frameColor=theme.accent_primary,
            frameSize=(-0.30, 0.30, -0.045, 0.05),
            pos=(0, 0, -0.63),
            relief=None,
            command=self.on_exit,
        )

    def show_vehicle(self, vehicle: Vehicle) -> None:
        """Populates panel with vehicle data and displays it."""
        self.active_vehicle = vehicle
        self.configurator.set_active_vehicle(vehicle)

        vdata = vehicle.data
        self.txt_title.setText(vdata.display_name)
        self.txt_subtitle.setText(f"{vdata.manufacturer} * {vdata.category} * {vdata.year}")
        self.txt_price.setText(f"${vdata.price_usd:,} MSRP")

        specs = vdata.specifications
        vals = [
            specs.engine,
            f"{specs.power_hp} HP",
            f"{specs.torque_nm} Nm",
            f"{specs.accel_0_100} s",
            f"{specs.top_speed_kmh} km/h",
            specs.drivetrain,
            specs.transmission,
        ]
        for label_widget, val_str in zip(self.spec_labels, vals):
            label_widget.setText(val_str)

        # Rebuild swatches
        for btn in self.swatch_buttons:
            btn.destroy()
        self.swatch_buttons.clear()

        colors = vdata.available_colors
        if colors:
            total = len(colors)
            spacing = 0.11
            start_x = -((total - 1) * spacing) * 0.5
            for i, c in enumerate(colors):
                r, g, b = c.rgb
                btn = DirectButton(
                    parent=self.color_swatch_frame,
                    frameColor=Vec4(r, g, b, 1.0),
                    frameSize=(-0.04, 0.04, -0.035, 0.035),
                    pos=(start_x + i * spacing, 0, 0),
                    relief=None,
                    command=self._apply_swatch_color,
                    extraArgs=[i],
                )
                self.swatch_buttons.append(btn)

        self.root.show()

    def _apply_swatch_color(self, index: int) -> None:
        self.configurator.set_color_by_index(index)

    def _set_finish(self, finish: str) -> None:
        self.configurator.set_finish(finish)

    def hide(self) -> None:
        self.root.hide()
        self.active_vehicle = None
