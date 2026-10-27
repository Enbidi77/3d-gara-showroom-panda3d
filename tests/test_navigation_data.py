"""Tests for showroom zones and navigation registry."""

import pytest

from panda_motors.world.showroom_zones import ShowroomZoneRegistry


@pytest.fixture
def zone_registry():
    return ShowroomZoneRegistry()


def test_zone_registry_loads_all_zones(zone_registry):
    zones = zone_registry.get_all_zones()
    assert len(zones) == 9
    zone_ids = [z.id for z in zones]
    expected = [
        "main_showroom",
        "hypercar_exhibition",
        "supercar_gallery",
        "luxury_collection",
        "electric_zone",
        "configurator_studio",
        "customer_lounge",
        "reception_center",
        "outdoor_display",
    ]
    for exp in expected:
        assert exp in zone_ids


def test_get_zone_by_id(zone_registry):
    z = zone_registry.get_zone("main_showroom")
    assert z is not None
    assert z.name == "Main Showroom"
    assert len(z.player_spawn) == 4
    assert len(z.camera_position) == 3


def test_nearest_zone(zone_registry):
    # At (0, -14), nearest should be main_showroom
    nearest = zone_registry.get_nearest_zone(0.0, -14.0)
    assert nearest is not None
    assert nearest.id == "main_showroom"

    # Near (12, 10), nearest should be hypercar_exhibition
    nearest_hyper = zone_registry.get_nearest_zone(10.0, 6.0)
    assert nearest_hyper is not None
    assert nearest_hyper.id == "hypercar_exhibition"
