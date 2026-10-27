"""Guided tour orchestrator managing waypoint progression, camera motion, and captions."""

import logging

from panda3d.core import Point3

from panda_motors.core.events import EventBus
from panda_motors.navigation.camera_controller import CameraController
from panda_motors.tours.tour_points import TOUR_WAYPOINTS, TourWaypoint

logger = logging.getLogger(__name__)


class TourManager:
    """Coordinates the cinematic guided showroom tour."""

    def __init__(self, camera_controller: CameraController) -> None:
        self.camera_controller = camera_controller
        self.waypoints: list[TourWaypoint] = list(TOUR_WAYPOINTS)
        self.current_index: int = 0
        self.is_active: bool = False
        self.is_paused: bool = False
        self._elapsed_time: float = 0.0
        self._waiting_at_point: bool = False
        self.event_bus = EventBus.get_instance()

    def start_tour(self, start_index: int = 0) -> None:
        """Starts guided tour from specified waypoint index."""
        self.is_active = True
        self.is_paused = False
        self.current_index = max(0, min(len(self.waypoints) - 1, start_index))
        self._elapsed_time = 0.0
        self._waiting_at_point = False
        self._move_to_waypoint(self.current_index)

    def stop_tour(self) -> None:
        """Exits guided tour and notifies application."""
        self.is_active = False
        self.is_paused = False
        self.event_bus.publish("on_tour_stopped")

    def toggle_pause(self) -> bool:
        """Pauses or resumes tour playback."""
        if self.is_active:
            self.is_paused = not self.is_paused
            return self.is_paused
        return False

    def next_waypoint(self) -> None:
        """Skips immediately to the next waypoint."""
        if not self.is_active:
            return
        if self.current_index < len(self.waypoints) - 1:
            self.current_index += 1
            self._move_to_waypoint(self.current_index)
        else:
            self.stop_tour()

    def previous_waypoint(self) -> None:
        """Returns to previous waypoint."""
        if not self.is_active:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._move_to_waypoint(self.current_index)

    def _move_to_waypoint(self, index: int) -> None:
        wp = self.waypoints[index]
        self._waiting_at_point = False
        self._elapsed_time = 0.0

        # Calculate target camera HPR looking at target
        cam_pos = Point3(*wp.camera_pos)
        target = Point3(*wp.look_target)

        dummy = self.camera_controller.camera.getParent().attachNewNode("tour_dummy")
        dummy.setPos(cam_pos)
        dummy.lookAt(target)
        target_hpr = dummy.getHpr()
        dummy.removeNode()

        self.event_bus.publish(
            "on_tour_waypoint_changed",
            index=index,
            total=len(self.waypoints),
            waypoint=wp,
        )

        def on_arrived():
            self._waiting_at_point = True
            self._elapsed_time = 0.0

        self.camera_controller.transition_to(
            cam_pos,
            target_hpr,
            duration=wp.transition_seconds,
            on_complete=on_arrived,
        )

    def update(self, dt: float) -> None:
        """Advances waypoint timer."""
        if not self.is_active or self.is_paused:
            return

        if self._waiting_at_point:
            self._elapsed_time += dt
            wp = self.waypoints[self.current_index]
            if self._elapsed_time >= wp.duration_seconds:
                self.next_waypoint()

    @property
    def current_waypoint(self) -> TourWaypoint | None:
        if self.is_active and 0 <= self.current_index < len(self.waypoints):
            return self.waypoints[self.current_index]
        return None
