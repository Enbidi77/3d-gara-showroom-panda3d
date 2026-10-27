"""Tests for state manager, event bus, and procedural fallback car."""

from panda_motors.app.state_manager import AppState, StateManager
from panda_motors.core.events import EventBus
from panda_motors.core.performance import PerformanceMonitor
from panda_motors.vehicles.procedural_car import create_procedural_car


def test_state_manager_transitions():
    sm = StateManager(AppState.MAIN_MENU)
    assert sm.current_state == AppState.MAIN_MENU

    sm.change_state(AppState.EXPLORATION)
    assert sm.current_state == AppState.EXPLORATION
    assert sm.previous_state == AppState.MAIN_MENU

    sm.change_state(AppState.INSPECTION)
    assert sm.current_state == AppState.INSPECTION

    sm.revert_to_previous()
    assert sm.current_state == AppState.EXPLORATION


def test_event_bus():
    bus = EventBus.get_instance()
    bus.clear()

    received = []
    def on_custom_event(**kwargs):
        received.append(kwargs)

    bus.subscribe("test_event", on_custom_event)
    bus.publish("test_event", message="hello", value=42)

    assert len(received) == 1
    assert received[0]["message"] == "hello"
    assert received[0]["value"] == 42


def test_performance_monitor():
    pm = PerformanceMonitor()
    assert pm.fps > 0
    assert pm.frame_time_ms > 0
    pm.update()


def test_procedural_car_creation():
    node = create_procedural_car("test_fallback_car")
    assert node is not None
    assert node.getNumChildren() >= 1
