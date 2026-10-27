"""Showroom zone definitions and spatial queries."""

import json
import math
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DisplayPlatformData:
    index: int
    radius: float
    position: tuple[float, float, float]
    name: str


@dataclass
class ShowroomZone:
    id: str
    name: str
    description: str
    camera_position: tuple[float, float, float]
    camera_target: tuple[float, float, float]
    player_spawn: tuple[float, float, float, float]
    display_platforms: list[DisplayPlatformData] = field(default_factory=list)
    tour_caption: str = ""
    category_filter: str = "All Cars"


class ShowroomZoneRegistry:
    """Registry of all distinct zones in Panda Motors showroom."""

    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            data_path = base_dir / "data" / "showroom_zones.json"

        self.zones: dict[str, ShowroomZone] = {}
        self.load_from_json(data_path)

    def load_from_json(self, path: Path) -> None:
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            platforms = [
                DisplayPlatformData(
                    index=p["index"],
                    radius=float(p["radius"]),
                    position=(float(p["position"][0]), float(p["position"][1]), float(p["position"][2])),
                    name=p["name"],
                )
                for p in item.get("display_platforms", [])
            ]
            zone = ShowroomZone(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                camera_position=tuple(item["camera_position"]),  # type: ignore
                camera_target=tuple(item["camera_target"]),  # type: ignore
                player_spawn=tuple(item["player_spawn"]),  # type: ignore
                display_platforms=platforms,
                tour_caption=item.get("tour_caption", ""),
                category_filter=item.get("category_filter", "All Cars"),
            )
            self.zones[zone.id] = zone

    def get_zone(self, zone_id: str) -> ShowroomZone | None:
        return self.zones.get(zone_id)

    def get_all_zones(self) -> list[ShowroomZone]:
        return list(self.zones.values())

    def get_nearest_zone(self, x: float, y: float) -> ShowroomZone | None:
        """Finds closest zone to the given coordinates."""
        best_zone = None
        min_dist = float("inf")
        for zone in self.zones.values():
            zx, zy = zone.player_spawn[0], zone.player_spawn[1]
            dist = math.hypot(x - zx, y - zy)
            if dist < min_dist:
                min_dist = dist
                best_zone = zone
        return best_zone
