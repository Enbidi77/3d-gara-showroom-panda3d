"""Event bus system for Panda Motors.

Enables decoupled communication across UI, gameplay, simulation, and rendering services.
"""

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    """Centralized publish-subscribe event dispatcher."""

    _instance = None

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    @classmethod
    def get_instance(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """Register a callback listener for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        if callback not in self._listeners[event_name]:
            self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """Unregister a callback listener."""
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """Dispatch an event with payload to all registered listeners."""
        if event_name in self._listeners:
            for callback in list(self._listeners[event_name]):
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(
                        f"Error invoking listener {callback} for event '{event_name}': {e}",
                        exc_info=True,
                    )

    def clear(self) -> None:
        """Clear all registered event listeners."""
        self._listeners.clear()
