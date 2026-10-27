"""Tests for configuration management and presets."""

import pytest

from panda_motors.app.config_manager import ConfigManager


@pytest.fixture
def config_mgr():
    return ConfigManager()


def test_app_config_loaded(config_mgr):
    name = config_mgr.get_app("app.name")
    assert name == "Panda Motors"
    tagline = config_mgr.get_app("app.tagline")
    assert "Explore" in tagline


def test_graphics_presets(config_mgr):
    high = config_mgr.get_graphics_preset("high")
    assert high is not None
    assert high["name"] == "High"
    assert high["shadows"] is True

    low = config_mgr.get_graphics_preset("low")
    assert low["shadows"] is False
    assert low["msaa_samples"] == 0

    ultra = config_mgr.get_graphics_preset("ultra")
    assert ultra["msaa_samples"] == 8


def test_controls_config(config_mgr):
    kb = config_mgr.get_controls("keyboard")
    assert kb["move_forward"] == "w"
    assert kb["move_backward"] == "s"
    assert kb["interact"] == "e"
    assert kb["toggle_camera"] == "f"
