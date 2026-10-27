"""Asset management system with caching and robust fallbacks."""

import logging
from pathlib import Path

from direct.showbase.Loader import Loader
from panda3d.core import (
    AudioSound,
    Filename,
    NodePath,
    SamplerState,
    Texture,
)

from panda_motors.vehicles.procedural_car import create_procedural_car

logger = logging.getLogger(__name__)


class AssetManager:
    """Handles loading, caching, and fallback substitution for 3D and 2D assets."""

    def __init__(self, loader: Loader, base_dir: Path | None = None) -> None:
        self.loader = loader
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

        self._model_cache: dict[str, NodePath] = {}
        self._texture_cache: dict[str, Texture] = {}
        self._sound_cache: dict[str, AudioSound] = {}

    def resolve_path(self, rel_path: str | Path) -> Path:
        """Resolve a relative path against workspace base directory."""
        p = Path(rel_path)
        if p.is_absolute():
            return p
        return self.base_dir / p

    def load_model(self, model_path: str | Path, use_cache: bool = True) -> NodePath:
        """Loads a 3D model (.bam, .glb, etc.) with automatic procedural fallback."""
        path_str = str(model_path)
        resolved = self.resolve_path(model_path)

        if use_cache and path_str in self._model_cache:
            instance = NodePath(f"instance_{Path(path_str).stem}")
            self._model_cache[path_str].copyTo(instance)
            return instance

        node: NodePath | None = None

        if resolved.exists():
            try:
                fn = Filename.fromOsSpecific(str(resolved))
                loaded = self.loader.loadModel(fn)
                if loaded is not None:
                    node = loaded
            except Exception as e:
                logger.warning(f"Error loading model from {resolved}: {e}. Trying fallback.")

        if node is None:
            # Fallback to BAM version if user gave GLB
            if str(resolved).endswith(".glb"):
                bam_path = resolved.with_suffix(".bam")
                if bam_path.exists():
                    try:
                        fn = Filename.fromOsSpecific(str(bam_path))
                        node = self.loader.loadModel(fn)
                    except Exception as e:
                        logger.warning(f"Failed to load bam fallback {bam_path}: {e}")

        # If still None, generate procedural fallback
        if node is None:
            logger.warning(f"Asset '{model_path}' not found or invalid; generating procedural vehicle.")
            node = create_procedural_car(name=f"fallback_{Path(path_str).stem}")

        if use_cache:
            self._model_cache[path_str] = node

        # Return a copy to avoid scene-graph conflicts
        instance = NodePath(f"instance_{Path(path_str).stem}")
        node.copyTo(instance)
        return instance

    def load_texture(
        self,
        texture_path: str | Path,
        min_filter=SamplerState.FT_linear_mipmap_linear,
        mag_filter=SamplerState.FT_linear,
        anisotropic_degree: int = 4,
    ) -> Texture | None:
        """Loads and configures a 2D texture map."""
        path_str = str(texture_path)
        if path_str in self._texture_cache:
            return self._texture_cache[path_str]

        resolved = self.resolve_path(texture_path)
        if not resolved.exists():
            logger.warning(f"Texture file not found: {resolved}")
            return None

        try:
            fn = Filename.fromOsSpecific(str(resolved))
            tex = self.loader.loadTexture(fn)
            if tex is not None:
                tex.setMinfilter(min_filter)
                tex.setMagfilter(mag_filter)
                tex.setAnisotropicDegree(anisotropic_degree)
                self._texture_cache[path_str] = tex
                return tex
        except Exception as e:
            logger.error(f"Failed to load texture {resolved}: {e}")

        return None

    def load_sound(self, sound_path: str | Path) -> AudioSound | None:
        """Loads an audio file with caching."""
        path_str = str(sound_path)
        if path_str in self._sound_cache:
            return self._sound_cache[path_str]

        resolved = self.resolve_path(sound_path)
        if not resolved.exists():
            return None

        try:
            fn = Filename.fromOsSpecific(str(resolved))
            snd = self.loader.loadSfx(fn)
            if snd:
                self._sound_cache[path_str] = snd
                return snd
        except Exception as e:
            logger.warning(f"Could not load audio {sound_path}: {e}")
        return None
