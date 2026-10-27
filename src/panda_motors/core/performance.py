"""Performance monitoring and graphics preset controller."""

from panda3d.core import ClockObject


class PerformanceMonitor:
    """Tracks FPS, delta time, and frame latency metrics."""

    def __init__(self) -> None:
        self.clock = ClockObject.getGlobalClock()
        self._fps: float = 60.0
        self._frame_time_ms: float = 16.6
        self._history_len = 60
        self._frame_times: list[float] = []

    def update(self) -> None:
        """Call each frame to sample timing statistics."""
        dt = self.clock.getDt()
        if dt > 0.0001:
            fps_current = 1.0 / dt
            self._fps = 0.9 * self._fps + 0.1 * fps_current
            self._frame_time_ms = dt * 1000.0

            self._frame_times.append(self._frame_time_ms)
            if len(self._frame_times) > self._history_len:
                self._frame_times.pop(0)

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def frame_time_ms(self) -> float:
        return self._frame_time_ms

    @property
    def avg_frame_time_ms(self) -> float:
        if not self._frame_times:
            return 16.6
        return sum(self._frame_times) / len(self._frame_times)
