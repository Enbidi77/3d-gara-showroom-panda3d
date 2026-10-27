"""Application state machine for Panda Motors."""

import logging
from enum import Enum, auto

from panda_motors.core.events import EventBus

logger = logging.getLogger(__name__)


class AppState(Enum):
    MAIN_MENU = auto()
    EXPLORATION = auto()
    INSPECTION = auto()
    CONFIGURATOR = auto()
    CATALOG_BROWSER = auto()
    GUIDED_TOUR = auto()
    SETTINGS = auto()


class StateManager:
    """Manages modal transitions between showroom modes."""

    def __init__(self, initial_state: AppState = AppState.MAIN_MENU) -> None:
        self._current_state: AppState = initial_state
        self._previous_state: AppState | None = None
        self._event_bus = EventBus.get_instance()

    @property
    def current_state(self) -> AppState:
        return self._current_state

    @property
    def previous_state(self) -> AppState | None:
        return self._previous_state

    def change_state(self, new_state: AppState, **context: object) -> bool:
        """Transitions to a new state and notifies listeners."""
        if new_state == self._current_state:
            return False

        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state

        logger.info(f"State transition: {old_state.name} -> {new_state.name}")
        self._event_bus.publish(
            "on_state_changed",
            old_state=old_state,
            new_state=new_state,
            context=context,
        )
        return True

    def revert_to_previous(self) -> bool:
        """Returns to the previous state if available."""
        if self._previous_state is not None:
            return self.change_state(self._previous_state)
        return self.change_state(AppState.EXPLORATION)
