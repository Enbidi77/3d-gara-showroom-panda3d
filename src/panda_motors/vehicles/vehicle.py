"""Vehicle data structures and dynamic material/appearance controller."""

import logging
from dataclasses import dataclass, field

from panda3d.core import Material, NodePath, Vec4

logger = logging.getLogger(__name__)


@dataclass
class VehicleColor:
    name: str
    hex: str
    rgb: tuple[float, float, float]
    finish: str = "metallic"  # "metallic", "matte", "gloss"


@dataclass
class VehicleSpecs:
    engine: str
    power_hp: int
    torque_nm: int
    top_speed_kmh: int
    accel_0_100: float
    drivetrain: str
    transmission: str
    weight_kg: int


@dataclass
class VehicleData:
    id: str
    manufacturer: str
    model: str
    year: int
    category: str
    display_name: str
    short_description: str
    specifications: VehicleSpecs
    price_usd: int
    asset_path: str
    scale: tuple[float, float, float]
    rotation_offset: tuple[float, float, float]
    position_offset: tuple[float, float, float]
    zone_id: str
    platform_index: int
    available_colors: list[VehicleColor]
    features: list[str] = field(default_factory=list)


class Vehicle:
    """Live interactive vehicle instance placed in the 3D scene."""

    def __init__(self, data: VehicleData, model_node: NodePath) -> None:
        self.data = data
        self.node = model_node
        self.current_color: VehicleColor = data.available_colors[0] if data.available_colors else VehicleColor("Default", "#FFFFFF", (1.0, 1.0, 1.0))
        self.current_finish: str = self.current_color.finish

        # Find or tag paintable nodes
        self._body_nodes: list[NodePath] = self._find_paintable_nodes()
        self.turntable_speed: float = 0.0  # degrees per second
        self.headlights_on: bool = False

        # Apply initial color
        self.apply_color(self.current_color)

    def _find_paintable_nodes(self) -> list[NodePath]:
        """Locates nodes responsible for car body paintwork."""
        paintable: list[NodePath] = []
        # Search for common automotive body naming conventions
        keywords = ["body", "paint", "carrosserie", "chassis", "car_body", "exterior", "shell"]

        for child in self.node.findAllMatches("**/+GeomNode"):
            name = child.getName().lower()
            if any(k in name for k in keywords):
                paintable.append(child)

        # If none matched specifically by name, default to the entire model root or first geom
        if not paintable:
            # Avoid glass/interior/wheel if possible, but fallback safely
            paintable = [self.node]

        return paintable

    def apply_color(self, color: VehicleColor) -> None:
        """Dynamically applies automotive paint color and finish to the 3D vehicle."""
        self.current_color = color
        self.current_finish = color.finish
        r, g, b = color.rgb
        color_vec = Vec4(r, g, b, 1.0)

        # Configure material properties based on finish
        mat = Material(f"{self.data.id}_paint_mat")
        mat.setDiffuse(color_vec)

        if color.finish == "metallic":
            mat.setSpecular(Vec4(0.9, 0.92, 0.96, 1.0))
            mat.setShininess(90.0)
            mat.setMetallic(0.85)
            mat.setRoughness(0.2)
        elif color.finish == "matte":
            mat.setSpecular(Vec4(0.15, 0.15, 0.15, 1.0))
            mat.setShininess(10.0)
            mat.setMetallic(0.1)
            mat.setRoughness(0.85)
        else:  # gloss
            mat.setSpecular(Vec4(1.0, 1.0, 1.0, 1.0))
            mat.setShininess(120.0)
            mat.setMetallic(0.2)
            mat.setRoughness(0.05)

        for np in self._body_nodes:
            np.setMaterial(mat, 1)
            np.setColorScale(color_vec, 1)

    def set_finish(self, finish: str) -> None:
        """Modifies paint finish: metallic, matte, or gloss."""
        new_color = VehicleColor(
            name=self.current_color.name,
            hex=self.current_color.hex,
            rgb=self.current_color.rgb,
            finish=finish,
        )
        self.apply_color(new_color)

    def update(self, dt: float) -> None:
        """Performs frame updates (e.g. turntable rotation)."""
        if abs(self.turntable_speed) > 0.001:
            self.node.setH(self.node.getH() + self.turntable_speed * dt)

    def toggle_headlights(self) -> bool:
        """Toggles vehicle lighting emission."""
        self.headlights_on = not self.headlights_on
        # Search for headlight nodes or apply emission
        for child in self.node.findAllMatches("**/+GeomNode"):
            if "light" in child.getName().lower() or "lamp" in child.getName().lower():
                if self.headlights_on:
                    child.setColorScale(Vec4(2.0, 2.0, 2.2, 1.0))
                else:
                    child.clearColorScale()
        return self.headlights_on
