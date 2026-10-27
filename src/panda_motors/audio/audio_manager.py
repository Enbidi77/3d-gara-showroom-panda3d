"""Audio manager controlling ambient loops, UI feedback, and vehicle engine sounds."""

import logging

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AudioSound

from panda_motors.core.asset_manager import AssetManager

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages audio playback, volumes, and sound effect triggers."""

    def __init__(self, base: ShowBase, asset_manager: AssetManager) -> None:
        self.base = base
        self.asset_manager = asset_manager

        self.master_volume: float = 0.8
        self.ambient_volume: float = 0.6
        self.sfx_volume: float = 0.7
        self.muted: bool = False

        self._ambient_sound: AudioSound | None = None
        self._init_ambient()

    def _init_ambient(self) -> None:
        """Loads and starts looping background showroom ambiance."""
        snd = self.asset_manager.load_sound("assets/audio/ambient_showroom.wav")
        if snd:
            snd.setLoop(True)
            snd.setVolume(self.master_volume * self.ambient_volume)
            snd.play()
            self._ambient_sound = snd

    def play_ui_click(self) -> None:
        """Plays crisp glass click feedback."""
        if self.muted:
            return
        snd = self.asset_manager.load_sound("assets/audio/ui_click.wav")
        if snd:
            snd.setVolume(self.master_volume * self.sfx_volume)
            snd.play()

    def play_ui_hover(self) -> None:
        """Plays soft hover feedback."""
        if self.muted:
            return
        snd = self.asset_manager.load_sound("assets/audio/ui_hover.wav")
        if snd:
            snd.setVolume(self.master_volume * self.sfx_volume * 0.5)
            snd.play()

    def play_engine_rev(self) -> None:
        """Plays vehicle engine start/rev sequence."""
        if self.muted:
            return
        snd = self.asset_manager.load_sound("assets/audio/car_engine.wav")
        if snd:
            snd.setVolume(self.master_volume * self.sfx_volume)
            snd.play()

    def set_volumes(self, master: float | None = None, ambient: float | None = None, sfx: float | None = None) -> None:
        """Updates sound volumes and adjusts active channels."""
        if master is not None:
            self.master_volume = max(0.0, min(1.0, master))
        if ambient is not None:
            self.ambient_volume = max(0.0, min(1.0, ambient))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))

        if self._ambient_sound:
            eff_vol = 0.0 if self.muted else self.master_volume * self.ambient_volume
            self._ambient_sound.setVolume(eff_vol)

    def toggle_mute(self) -> bool:
        """Toggles audio mute state."""
        self.muted = not self.muted
        self.set_volumes()
        return self.muted
