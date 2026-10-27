"""Camera controller supporting smooth transitions, cinematic modes, and collision avoidance."""

import logging
from collections.abc import Callable

from panda3d.core import NodePath, Point3, Vec3

logger = logging.getLogger(__name__)


class CameraController:
    """Provides smooth cinematic interpolations and camera animations."""

    def __init__(self, camera: NodePath) -> None:
        self.camera = camera
        self._is_transitioning: bool = False
        self._start_pos = Point3(0, 0, 0)
        self._target_pos = Point3(0, 0, 0)
        self._start_hpr = Vec3(0, 0, 0)
        self._target_hpr = Vec3(0, 0, 0)
        self._transition_duration: float = 1.0
        self._transition_time: float = 0.0
        self._on_complete: Callable[[], None] | None = None

    def transition_to(
        self,
        target_pos: Point3,
        target_hpr: Vec3,
        duration: float = 1.5,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        """Starts a smooth cubic hermite / smoothstep transition to target pos and hpr."""
        self._is_transitioning = True
        self._start_pos = Point3(self.camera.getPos())
        self._target_pos = Point3(target_pos)
        self._start_hpr = Vec3(self.camera.getHpr())
        self._target_hpr = Vec3(target_hpr)
        self._transition_duration = max(0.1, duration)
        self._transition_time = 0.0
        self._on_complete = on_complete

    def update(self, dt: float) -> bool:
        """Updates active transitions. Returns True if transition is active."""
        if not self._is_transitioning:
            return False

        self._transition_time += dt
        t = min(1.0, self._transition_time / self._transition_duration)
        # Smoothstep curve: 3t^2 - 2t^3
        smooth_t = t * t * (3.0 - 2.0 * t)

        current_pos = self._start_pos + (self._target_pos - self._start_pos) * smooth_t

        # Angle shortest path interpolation
        dh = (self._target_hpr.getX() - self._start_hpr.getX() + 180.0) % 360.0 - 180.0
        dp = self._target_hpr.getY() - self._start_hpr.getY()
        dr = self._target_hpr.getZ() - self._start_hpr.getZ()

        current_h = self._start_hpr.getX() + dh * smooth_t
        current_p = self._start_hpr.getY() + dp * smooth_t
        current_r = self._start_hpr.getZ() + dr * smooth_t

        self.camera.setPos(current_pos)
        self.camera.setHpr(current_h, current_p, current_r)

        if t >= 1.0:
            self._is_transitioning = False
            if self._on_complete:
                cb = self._on_complete
                self._on_complete = None
                cb()

        return self._is_transitioning
