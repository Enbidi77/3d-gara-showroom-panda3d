"""Configuration manager for Panda Motors."""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Loads and caches TOML/JSON configuration settings with runtime mutation."""

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            # Workspace root
            self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.config_dir = self.base_dir / "config"
        self.app_config: dict[str, Any] = {}
        self.graphics_config: dict[str, Any] = {}
        self.controls_config: dict[str, Any] = {}

        self.reload_all()

    def _read_toml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            logger.warning(f"Config file not found: {path}")
            return {}
        if tomllib is None:
            logger.warning("tomllib not available, returning empty configuration")
            return {}
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            logger.error(f"Failed to parse TOML {path}: {e}")
            return {}

    def reload_all(self) -> None:
        """Reload all configuration files from disk."""
        self.app_config = self._read_toml(self.config_dir / "app.toml")
        self.graphics_config = self._read_toml(self.config_dir / "graphics.toml")
        self.controls_config = self._read_toml(self.config_dir / "controls.toml")

    def get_app(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val: Any = self.app_config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def get_graphics_preset(self, preset_name: str | None = None) -> dict[str, Any]:
        presets = self.graphics_config.get("presets", {})
        if preset_name is None:
            preset_name = self.graphics_config.get("active", {}).get("preset", "high")
        return presets.get(preset_name, presets.get("high", {}))

    def get_controls(self, section: str = "keyboard") -> dict[str, Any]:
        return self.controls_config.get(section, {})
