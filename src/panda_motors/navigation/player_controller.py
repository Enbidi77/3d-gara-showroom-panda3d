"""Controllable player avatar with smooth 1st/3rd person navigation and collision."""

import logging
import math

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    NodePath,
    Point3,
    Vec3,
)

from panda_motors.core.asset_manager import AssetManager
from panda_motors.world.collision_world import CollisionWorld

logger = logging.getLogger(__name__)


class PlayerController:
    """Handles keyboard/mouse movement, physics collisions, and camera switching."""

    def __init__(
        self,
        base: ShowBase,
        collision_world: CollisionWorld,
        asset_manager: AssetManager,
        start_pos: Point3 = Point3(0, -14, 0),
    ) -> None:
        self.base = base
        self.collision_world = collision_world
        self.asset_manager = asset_manager

        # Root character node
        self.root = base.render.attachNewNode("player_root")
        self.root.setPos(start_pos)
        self.root.setH(0.0)

        # Character visual model
        self.character_model: NodePath | None = None
        self._load_character_model()

        # Collision setup
        self.col_np = collision_world.register_player_collider(self.root, radius=0.45, height=1.7)
        self.probe_np = collision_world.register_player_interaction_probe(self.root)

        # Camera settings
        self.is_first_person: bool = False
        self.mouse_sensitivity_x: float = 0.15
        self.mouse_sensitivity_y: float = 0.12
        self.pitch: float = -5.0
        self.yaw: float = 0.0

        # Movement physics
        self.walk_speed: float = 4.2      # m/s
        self.sprint_speed: float = 7.5    # m/s
        self.velocity = Vec3(0, 0, 0)
        self.acceleration: float = 18.0
        self.deceleration: float = 14.0

        # Input states
        self.key_states: dict[str, bool] = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "sprint": False,
        }
        self.mouse_look_enabled: bool = False
        self._step_timer: float = 0.0

    def _load_character_model(self) -> None:
        """Loads and positions character mesh."""
        try:
            self.character_model = self.asset_manager.load_model("assets/models/characters/xbot.bam")
            self.character_model.reparentTo(self.root)
            self.character_model.setScale(1.0)
            self.character_model.setH(180.0)  # Face forward
            self.character_model.setPos(0, 0, 0)
        except Exception as e:
            logger.warning(f"Failed to load character model: {e}")

    def set_key_state(self, key: str, pressed: bool) -> None:
        if key in self.key_states:
            self.key_states[key] = pressed

    def toggle_perspective(self) -> bool:
        """Toggles between third-person and first-person perspective."""
        self.is_first_person = not self.is_first_person
        if self.character_model:
            if self.is_first_person:
                self.character_model.hide()
            else:
                self.character_model.show()
        return self.is_first_person

    def handle_mouse_move(self, dx: float, dy: float) -> None:
        """Applies mouse delta to yaw and pitch."""
        if not self.mouse_look_enabled:
            return

        self.yaw = (self.yaw - dx * self.mouse_sensitivity_x) % 360.0
        self.pitch = max(-60.0, min(60.0, self.pitch - dy * self.mouse_sensitivity_y))
        self.root.setH(self.yaw)

    def teleport(self, x: float, y: float, z: float, heading: float) -> None:
        """Teleports player to coordinates and resets velocity."""
        self.root.setPos(x, y, z)
        self.yaw = heading
        self.pitch = -5.0
        self.root.setH(heading)
        self.velocity = Vec3(0, 0, 0)

    def update(self, dt: float) -> None:
        """Simulates player movement and collision traversal."""
        # Calculate target movement direction relative to camera heading
        move_dir = Vec3(0, 0, 0)
        if self.key_states["forward"]:
            move_dir += Vec3(0, 1, 0)
        if self.key_states["backward"]:
            move_dir += Vec3(0, -1, 0)
        if self.key_states["left"]:
            move_dir += Vec3(-1, 0, 0)
        if self.key_states["right"]:
            move_dir += Vec3(1, 0, 0)

        if move_dir.lengthSquared() > 0.001:
            move_dir.normalize()
            # Rotate by character heading
            rad_h = math.radians(self.yaw)
            world_dir = Vec3(
                move_dir.getX() * math.cos(rad_h) - move_dir.getY() * math.sin(rad_h),
                move_dir.getX() * math.sin(rad_h) + move_dir.getY() * math.cos(rad_h),
                0,
            )

            max_speed = self.sprint_speed if self.key_states["sprint"] else self.walk_speed
            target_vel = world_dir * max_speed

            # Accelerate towards target velocity
            diff = target_vel - self.velocity
            step = self.acceleration * dt
            if diff.length() <= step:
                self.velocity = target_vel
            else:
                self.velocity += diff.normalized() * step

            # Step audio timer
            self._step_timer += dt
            step_interval = 0.32 if self.key_states["sprint"] else 0.48
            if self._step_timer >= step_interval:
                self._step_timer = 0.0
                snd = self.asset_manager.load_sound("assets/audio/footstep.wav")
                if snd:
                    snd.setVolume(0.35)
                    snd.play()
        else:
            # Decelerate to stop
            v_len = self.velocity.length()
            if v_len > 0.001:
                decay = self.deceleration * dt
                if v_len <= decay:
                    self.velocity = Vec3(0, 0, 0)
                else:
                    self.velocity -= self.velocity.normalized() * decay

        # Apply displacement
        if self.velocity.lengthSquared() > 0.0001:
            current_pos = self.root.getPos()
            new_pos = current_pos + self.velocity * dt
            # Keep on ground level
            new_pos.setZ(0.0)
            self.root.setPos(new_pos)

        # Run Panda3D collision detection and push-out
        self.collision_world.traverser.traverse(self.base.render)

        # Update camera position based on perspective
        self._update_camera()

    def _update_camera(self) -> None:
        """Positions camera based on 1st vs 3rd person perspective."""
        p_pos = self.root.getPos()
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        if self.is_first_person:
            cam_pos = Point3(p_pos.getX(), p_pos.getY(), p_pos.getZ() + 1.68)
            self.base.cam.setPos(cam_pos)
            self.base.cam.setHpr(self.yaw, self.pitch, 0)
        else:
            # Third-person camera: 3.8m behind and 1.8m above character
            dist = 3.8
            height = 1.8
            cx = p_pos.getX() - dist * math.sin(rad_yaw) * math.cos(rad_pitch)
            cy = p_pos.getY() - dist * math.cos(rad_yaw) * math.cos(rad_pitch)
            cz = p_pos.getZ() + height + dist * math.sin(rad_pitch)

            self.base.cam.setPos(cx, cy, cz)
            target = Point3(p_pos.getX(), p_pos.getY(), p_pos.getZ() + 1.4)
            self.base.cam.lookAt(target)

    @property
    def position(self) -> Point3:
        return self.root.getPos()
