"""Loads and positions vehicle models in the showroom scene."""

import logging

from panda3d.core import NodePath

from panda_motors.core.asset_manager import AssetManager
from panda_motors.vehicles.vehicle import Vehicle
from panda_motors.vehicles.vehicle_catalog import VehicleCatalog
from panda_motors.world.collision_world import CollisionWorld

logger = logging.getLogger(__name__)


class VehicleLoader:
    """Instantiates 3D vehicle assets onto showroom display platforms."""

    def __init__(
        self,
        render: NodePath,
        asset_manager: AssetManager,
        catalog: VehicleCatalog,
        collision_world: CollisionWorld,
    ) -> None:
        self.render = render
        self.asset_manager = asset_manager
        self.catalog = catalog
        self.collision_world = collision_world

        self.vehicles_root = render.attachNewNode("vehicles_root")
        self.live_vehicles: dict[str, Vehicle] = {}

    def spawn_all_vehicles(self, platform_transforms: list[tuple[float, float, float, float]]) -> dict[str, Vehicle]:
        """Loads and positions all vehicles on their assigned display platforms."""
        for vdata in self.catalog.get_all():
            idx = vdata.platform_index
            if idx < len(platform_transforms):
                px, py, pradius, pheight = platform_transforms[idx]
            else:
                px, py, pradius, pheight = 0.0, 0.0, 4.0, 0.18

            # Calculate vehicle anchor position (raised slightly above platform top)
            ox, oy, oz = vdata.position_offset
            spawn_pos = (px + ox, py + oy, pheight + oz)

            try:
                # Load model via asset manager (with fallback protection)
                model_node = self.asset_manager.load_model(vdata.asset_path)
                model_node.reparentTo(self.vehicles_root)
                model_node.setPos(*spawn_pos)

                # Apply scaling
                sx, sy, sz = vdata.scale
                model_node.setScale(sx, sy, sz)

                # Apply rotation
                rx, ry, rz = vdata.rotation_offset
                model_node.setHpr(rx, ry, rz)

                # Wrap in live Vehicle instance
                veh = Vehicle(vdata, model_node)
                self.live_vehicles[vdata.id] = veh

                # Register collision obstacle and interaction proximity trigger
                self.collision_world.register_vehicle_obstacle(vdata.id, spawn_pos, radius=pradius * 0.9)

                logger.info(f"Spawned vehicle {vdata.id} on platform {idx} at {spawn_pos}")
            except Exception as e:
                logger.error(f"Failed to spawn vehicle {vdata.id}: {e}", exc_info=True)

        return self.live_vehicles

    def get_live_vehicle(self, vehicle_id: str) -> Vehicle | None:
        return self.live_vehicles.get(vehicle_id)

    def update_all(self, dt: float) -> None:
        """Updates animation/turntables for all active vehicles."""
        for veh in self.live_vehicles.values():
            veh.update(dt)
