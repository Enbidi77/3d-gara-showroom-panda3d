"""Vehicle catalog registry, search, filtering, and comparison service."""

import json
import logging
from pathlib import Path

from panda_motors.vehicles.vehicle import VehicleColor, VehicleData, VehicleSpecs

logger = logging.getLogger(__name__)


class VehicleCatalog:
    """Manages vehicle catalog metadata, search queries, filtering, and favorites."""

    def __init__(self, json_path: Path | None = None) -> None:
        if json_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            json_path = base_dir / "data" / "vehicles.json"

        self._vehicles: dict[str, VehicleData] = {}
        self._favorites: set[str] = set()
        self.load_from_json(json_path)

    def load_from_json(self, path: Path) -> None:
        """Parses vehicle definitions from JSON file."""
        if not path.exists():
            logger.warning(f"Vehicles data file not found: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            specs = VehicleSpecs(
                engine=item["specifications"]["engine"],
                power_hp=int(item["specifications"]["power_hp"]),
                torque_nm=int(item["specifications"]["torque_nm"]),
                top_speed_kmh=int(item["specifications"]["top_speed_kmh"]),
                accel_0_100=float(item["specifications"]["accel_0_100"]),
                drivetrain=item["specifications"]["drivetrain"],
                transmission=item["specifications"]["transmission"],
                weight_kg=int(item["specifications"]["weight_kg"]),
            )

            colors = [
                VehicleColor(
                    name=c["name"],
                    hex=c["hex"],
                    rgb=(float(c["rgb"][0]), float(c["rgb"][1]), float(c["rgb"][2])),
                    finish=c.get("finish", "metallic"),
                )
                for c in item.get("available_colors", [])
            ]

            veh_data = VehicleData(
                id=item["id"],
                manufacturer=item["manufacturer"],
                model=item["model"],
                year=int(item["year"]),
                category=item["category"],
                display_name=item["display_name"],
                short_description=item["short_description"],
                specifications=specs,
                price_usd=int(item["price_usd"]),
                asset_path=item["asset_path"],
                scale=tuple(item["scale"]),  # type: ignore
                rotation_offset=tuple(item["rotation_offset"]),  # type: ignore
                position_offset=tuple(item["position_offset"]),  # type: ignore
                zone_id=item["zone_id"],
                platform_index=int(item["platform_index"]),
                available_colors=colors,
                features=item.get("features", []),
            )
            self._vehicles[veh_data.id] = veh_data

    def get_vehicle(self, vehicle_id: str) -> VehicleData | None:
        return self._vehicles.get(vehicle_id)

    def get_all(self) -> list[VehicleData]:
        return list(self._vehicles.values())

    def get_by_category(self, category: str) -> list[VehicleData]:
        if category in ("All", "All Cars", ""):
            return self.get_all()
        return [v for v in self._vehicles.values() if v.category.lower() == category.lower()]

    def search(self, query: str, category: str | None = None) -> list[VehicleData]:
        """Filters vehicles by search query substring in name, manufacturer, or model."""
        vehicles = self.get_by_category(category) if category else self.get_all()
        if not query:
            return vehicles

        q = query.lower()
        return [
            v for v in vehicles
            if q in v.display_name.lower() or q in v.manufacturer.lower() or q in v.model.lower() or q in v.category.lower()
        ]

    def sort_by(self, vehicles: list[VehicleData], criterion: str, reverse: bool = False) -> list[VehicleData]:
        """Sorts vehicle list by power, acceleration, top speed, or price."""
        if criterion == "power":
            return sorted(vehicles, key=lambda v: v.specifications.power_hp, reverse=not reverse)
        elif criterion == "accel":
            return sorted(vehicles, key=lambda v: v.specifications.accel_0_100, reverse=reverse)
        elif criterion == "top_speed":
            return sorted(vehicles, key=lambda v: v.specifications.top_speed_kmh, reverse=not reverse)
        elif criterion == "price":
            return sorted(vehicles, key=lambda v: v.price_usd, reverse=not reverse)
        elif criterion == "name":
            return sorted(vehicles, key=lambda v: v.display_name, reverse=reverse)
        return vehicles

    def toggle_favorite(self, vehicle_id: str) -> bool:
        """Toggles favorite status and returns new state."""
        if vehicle_id in self._favorites:
            self._favorites.remove(vehicle_id)
            return False
        else:
            self._favorites.add(vehicle_id)
            return True

    def is_favorite(self, vehicle_id: str) -> bool:
        return vehicle_id in self._favorites

    def get_favorites(self) -> list[VehicleData]:
        return [v for v in self._vehicles.values() if v.id in self._favorites]

    def compare_vehicles(self, vehicle_ids: list[str]) -> list[VehicleData]:
        """Returns vehicle entries for side-by-side comparison."""
        return [self._vehicles[vid] for vid in vehicle_ids if vid in self._vehicles]
