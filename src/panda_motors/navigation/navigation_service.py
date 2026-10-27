"""Navigation service coordinating zone fast travel, waypoint routes, and zone transitions."""

import logging
from collections.abc import Callable

from panda3d.core import Point3

from panda_motors.core.events import EventBus
from panda_motors.navigation.camera_controller import CameraController
from panda_motors.navigation.player_controller import PlayerController
from panda_motors.world.showroom_zones import ShowroomZone, ShowroomZoneRegistry

logger = logging.getLogger(__name__)


class NavigationService:
    """Manages player travel across showroom zones."""

    def __init__(
        self,
        zone_registry: ShowroomZoneRegistry,
        player_controller: PlayerController,
        camera_controller: CameraController,
    ) -> None:
        self.zone_registry = zone_registry
        self.player_controller = player_controller
        self.camera_controller = camera_controller
        self.event_bus = EventBus.get_instance()

        self.current_zone: ShowroomZone | None = zone_registry.get_zone("main_showroom")

    def travel_to_zone(self, zone_id: str, smooth: bool = True, on_complete: Callable[[], None] | None = None) -> bool:
        """Navigates player and camera to target showroom zone."""
        zone = self.zone_registry.get_zone(zone_id)
        if not zone:
            logger.warning(f"Target zone '{zone_id}' not found.")
            return False

        old_zone = self.current_zone
        self.current_zone = zone

        sx, sy, sz, sh = zone.player_spawn

        if smooth:
            # Teleport player to destination
            self.player_controller.teleport(sx, sy, sz, sh)
            # Smooth camera transition into new zone
            cam_pos = Point3(*zone.camera_position)
            # Calculate target HPR by looking at camera_target
            dummy = self.camera_controller.camera.getParent().attachNewNode("dummy_calc")
            dummy.setPos(cam_pos)
            dummy.lookAt(Point3(*zone.camera_target))
            target_hpr = dummy.getHpr()
            dummy.removeNode()

            def finish():
                self.event_bus.publish("on_zone_changed", old_zone=old_zone, new_zone=zone)
                if on_complete:
                    on_complete()

            self.camera_controller.transition_to(cam_pos, target_hpr, duration=1.8, on_complete=finish)
        else:
            self.player_controller.teleport(sx, sy, sz, sh)
            self.event_bus.publish("on_zone_changed", old_zone=old_zone, new_zone=zone)
            if on_complete:
                on_complete()

        return True

    def update(self) -> None:
        """Updates zone detection based on player's live position."""
        pos = self.player_controller.position
        nearest = self.zone_registry.get_nearest_zone(pos.getX(), pos.getY())
        if nearest and nearest != self.current_zone:
            old = self.current_zone
            self.current_zone = nearest
            self.event_bus.publish("on_zone_changed", old_zone=old, new_zone=nearest)
