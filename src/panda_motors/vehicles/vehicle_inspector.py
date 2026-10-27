"""Vehicle inspection controller with orbit camera and detail viewpoints."""

import logging
import math

from panda3d.core import NodePath, Point3, Vec3

from panda_motors.vehicles.vehicle import Vehicle

logger = logging.getLogger(__name__)


class VehicleInspector:
    """Manages the focused inspection mode for a selected vehicle."""

    def __init__(self, camera: NodePath) -> None:
        self.camera = camera
        self.target_vehicle: Vehicle | None = None

        # Orbit camera parameters
        self.orbit_center = Point3(0, 0, 0.8)
        self.orbit_yaw: float = 45.0      # degrees
        self.orbit_pitch: float = 18.0    # degrees
        self.orbit_distance: float = 5.5  # meters
        self.turntable_active: bool = False

        # Previous exploration camera state
        self.saved_cam_pos = Point3(0, 0, 0)
        self.saved_cam_hpr = Vec3(0, 0, 0)

    def enter_inspection(self, vehicle: Vehicle) -> None:
        """Transitions into inspection mode for the specified vehicle."""
        self.target_vehicle = vehicle
        self.saved_cam_pos = Point3(self.camera.getPos())
        self.saved_cam_hpr = Vec3(self.camera.getHpr())

        # Set orbit center to vehicle world position
        v_pos = vehicle.node.getPos()
        self.orbit_center = Point3(v_pos.getX(), v_pos.getY(), v_pos.getZ() + 0.8)
        self.orbit_yaw = 45.0
        self.orbit_pitch = 18.0
        self.orbit_distance = 5.5
        self.turntable_active = False

        self._update_camera_transform()

    def exit_inspection(self) -> None:
        """Restores previous exploration camera state."""
        if self.target_vehicle and self.turntable_active:
            self.target_vehicle.turntable_speed = 0.0

        self.camera.setPos(self.saved_cam_pos)
        self.camera.setHpr(self.saved_cam_hpr)
        self.target_vehicle = None

    def rotate_orbit(self, delta_yaw: float, delta_pitch: float) -> None:
        """Rotates orbit camera with mouse drag."""
        self.orbit_yaw = (self.orbit_yaw - delta_yaw) % 360.0
        self.orbit_pitch = max(5.0, min(80.0, self.orbit_pitch + delta_pitch))
        self._update_camera_transform()

    def zoom_orbit(self, delta_zoom: float) -> None:
        """Zooms camera closer or further."""
        self.orbit_distance = max(2.5, min(10.0, self.orbit_distance - delta_zoom))
        self._update_camera_transform()

    def set_viewpoint(self, preset: str) -> None:
        """Snaps camera to preset viewpoints (Front, Rear, Side, Wheel, Top)."""
        presets = {
            "front": (0.0, 15.0, 5.0),
            "rear": (180.0, 15.0, 5.0),
            "side": (90.0, 12.0, 5.2),
            "wheel": (65.0, 8.0, 3.2),
            "top": (45.0, 75.0, 7.0),
        }
        if preset in presets:
            self.orbit_yaw, self.orbit_pitch, self.orbit_distance = presets[preset]
            self._update_camera_transform()

    def toggle_turntable(self) -> bool:
        """Toggles slow turntable rotation of vehicle."""
        if self.target_vehicle:
            self.turntable_active = not self.turntable_active
            self.target_vehicle.turntable_speed = 15.0 if self.turntable_active else 0.0
            return self.turntable_active
        return False

    def toggle_headlights(self) -> bool:
        """Toggles vehicle head/tail lights."""
        if self.target_vehicle:
            return self.target_vehicle.toggle_headlights()
        return False

    def _update_camera_transform(self) -> None:
        """Recomputes spherical coordinates and sets camera position and orientation."""
        rad_yaw = math.radians(self.orbit_yaw)
        rad_pitch = math.radians(self.orbit_pitch)

        cx = self.orbit_center.getX() + self.orbit_distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        cy = self.orbit_center.getY() - self.orbit_distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        cz = self.orbit_center.getZ() + self.orbit_distance * math.sin(rad_pitch)

        self.camera.setPos(cx, cy, cz)
        self.camera.lookAt(self.orbit_center)
