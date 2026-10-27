"""Interactive vehicle configuration studio controller."""

import logging

from panda_motors.core.events import EventBus
from panda_motors.vehicles.vehicle import Vehicle, VehicleColor

logger = logging.getLogger(__name__)


class VehicleConfigurator:
    """Manages real-time material, color, and finish tailoring for vehicles."""

    def __init__(self) -> None:
        self.active_vehicle: Vehicle | None = None
        self.default_color: VehicleColor | None = None
        self.event_bus = EventBus.get_instance()

    def set_active_vehicle(self, vehicle: Vehicle) -> None:
        """Sets target vehicle for configuration studio."""
        self.active_vehicle = vehicle
        if vehicle.data.available_colors:
            self.default_color = vehicle.data.available_colors[0]

    def set_color_by_index(self, index: int) -> bool:
        """Applies color from the vehicle's predefined catalog list."""
        if not self.active_vehicle or not self.active_vehicle.data.available_colors:
            return False
        colors = self.active_vehicle.data.available_colors
        if 0 <= index < len(colors):
            selected = colors[index]
            self.active_vehicle.apply_color(selected)
            self.event_bus.publish(
                "on_vehicle_configured",
                vehicle_id=self.active_vehicle.data.id,
                color=selected,
            )
            return True
        return False

    def set_finish(self, finish: str) -> bool:
        """Changes finish to metallic, matte, or gloss."""
        if not self.active_vehicle:
            return False
        if finish not in ("metallic", "matte", "gloss"):
            return False
        self.active_vehicle.set_finish(finish)
        self.event_bus.publish(
            "on_vehicle_configured",
            vehicle_id=self.active_vehicle.data.id,
            finish=finish,
        )
        return True

    def reset_to_default(self) -> None:
        """Restores original factory color and finish."""
        if self.active_vehicle and self.default_color:
            self.active_vehicle.apply_color(self.default_color)
            self.event_bus.publish(
                "on_vehicle_configured",
                vehicle_id=self.active_vehicle.data.id,
                color=self.default_color,
            )
