"""Settings panel for graphics presets, audio volumes, and UI themes."""

from collections.abc import Callable

from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText
from panda3d.core import NodePath, TextNode, Vec4

from panda_motors.audio.audio_manager import AudioManager
from panda_motors.ui.theme_manager import ThemeManager


class SettingsPanel:
    """Showroom configuration modal for graphics, audio, and visual appearance."""

    def __init__(
        self,
        parent_2d: NodePath,
        theme_manager: ThemeManager,
        audio_manager: AudioManager,
        on_preset_change: Callable[[str], None],
        on_toggle_theme: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        self.root = parent_2d.attachNewNode("settings_root")
        self.theme_manager = theme_manager
        self.audio_manager = audio_manager
        self.on_preset_change = on_preset_change
        self.on_toggle_theme = on_toggle_theme
        self.on_close = on_close

        self.current_preset = "high"
        self._build_panel()
        self.root.hide()

    def _build_panel(self) -> None:
        theme = self.theme_manager.current

        self.backdrop = DirectFrame(
            parent=self.root,
            frameColor=Vec4(0.05, 0.06, 0.09, 0.94),
            frameSize=(-0.75, 0.75, -0.75, 0.75),
            pos=(0, 0, 0),
        )

        OnscreenText(
            text="SETTINGS & PREFERENCES",
            parent=self.backdrop,
            pos=(0, 0.62),
            scale=0.044,
            fg=theme.text_primary,
            align=TextNode.ACenter,
            mayChange=False,
        )

        # 1. Section: Graphics Presets
        OnscreenText(
            text="GRAPHICS PRESET",
            parent=self.backdrop,
            pos=(-0.60, 0.46),
            scale=0.028,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        presets = ["Low", "Medium", "High", "Ultra"]
        self.preset_buttons = {}
        for i, pname in enumerate(presets):
            btn = DirectButton(
                parent=self.backdrop,
                text=pname,
                text_scale=0.028,
                text_fg=theme.text_primary if pname.lower() == "high" else theme.text_secondary,
                text_pos=(0, -0.01),
                frameColor=theme.accent_primary if pname.lower() == "high" else theme.bg_card,
                frameSize=(-0.11, 0.11, -0.03, 0.035),
                pos=(-0.45 + i * 0.28, 0, 0.38),
                relief=None,
                command=self._set_graphics_preset,
                extraArgs=[pname.lower()],
            )
            self.preset_buttons[pname.lower()] = btn

        # 2. Section: Audio Volume
        OnscreenText(
            text="AUDIO CONTROLS",
            parent=self.backdrop,
            pos=(-0.60, 0.24),
            scale=0.028,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )

        # Master Mute Toggle
        self.btn_mute = DirectButton(
            parent=self.backdrop,
            text="Audio: Enabled",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.16, 0.16, -0.03, 0.035),
            pos=(-0.35, 0, 0.15),
            relief=None,
            command=self._toggle_audio_mute,
        )

        # Ambient Volume +/-
        OnscreenText(
            text="Ambient Showroom Sound:",
            parent=self.backdrop,
            pos=(-0.60, 0.05),
            scale=0.026,
            fg=theme.text_secondary,
            align=TextNode.ALeft,
        )
        DirectButton(
            parent=self.backdrop,
            text="[ - ]",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.05, 0.05, -0.025, 0.028),
            pos=(0.20, 0, 0.05),
            relief=None,
            command=lambda: self.audio_manager.set_volumes(ambient=self.audio_manager.ambient_volume - 0.15),
        )
        DirectButton(
            parent=self.backdrop,
            text="[ + ]",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.05, 0.05, -0.025, 0.028),
            pos=(0.35, 0, 0.05),
            relief=None,
            command=lambda: self.audio_manager.set_volumes(ambient=self.audio_manager.ambient_volume + 0.15),
        )

        # 3. Section: UI Appearance
        OnscreenText(
            text="VISUAL THEME",
            parent=self.backdrop,
            pos=(-0.60, -0.12),
            scale=0.028,
            fg=theme.accent_primary,
            align=TextNode.ALeft,
            mayChange=False,
        )
        self.btn_theme = DirectButton(
            parent=self.backdrop,
            text=f"Theme: {self.theme_manager.current.name}",
            text_scale=0.028,
            text_fg=theme.text_primary,
            text_pos=(0, -0.01),
            frameColor=theme.bg_card,
            frameSize=(-0.22, 0.22, -0.03, 0.035),
            pos=(-0.30, 0, -0.20),
            relief=None,
            command=self._toggle_theme,
        )

        # 4. Controls summary
        OnscreenText(
            text="CONTROLS: WASD to Move, Mouse to Look, E to Interact, F for 1st/3rd Person",
            parent=self.backdrop,
            pos=(0, -0.38),
            scale=0.022,
            fg=theme.text_dim,
            align=TextNode.ACenter,
        )

        # Close / Return
        DirectButton(
            parent=self.backdrop,
            text="Save & Close [Esc]",
            text_scale=0.032,
            text_fg=Vec4(1, 1, 1, 1),
            text_pos=(0, -0.01),
            frameColor=theme.accent_primary,
            frameSize=(-0.20, 0.20, -0.035, 0.04),
            pos=(0, 0, -0.58),
            relief=None,
            command=self.on_close,
        )

    def _set_graphics_preset(self, preset: str) -> None:
        self.current_preset = preset
        theme = self.theme_manager.current
        for p, btn in self.preset_buttons.items():
            if p == preset:
                btn["frameColor"] = theme.accent_primary
                btn["text_fg"] = theme.text_primary
            else:
                btn["frameColor"] = theme.bg_card
                btn["text_fg"] = theme.text_secondary
        self.on_preset_change(preset)

    def _toggle_audio_mute(self) -> None:
        muted = self.audio_manager.toggle_mute()
        self.btn_mute["text"] = "Audio: Muted" if muted else "Audio: Enabled"

    def _toggle_theme(self) -> None:
        self.on_toggle_theme()
        self.btn_theme["text"] = f"Theme: {self.theme_manager.current.name}"

    def show(self) -> None:
        self.root.show()

    def hide(self) -> None:
        self.root.hide()

    def toggle(self) -> bool:
        if self.root.isHidden():
            self.show()
            return True
        else:
            self.hide()
            return False
