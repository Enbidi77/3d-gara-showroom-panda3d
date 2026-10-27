"""Collision geometry, collision traverser, and interaction trigger system."""

import logging

from panda3d.core import (
    BitMask32,
    CollisionBox,
    CollisionCapsule,
    CollisionHandlerPusher,
    CollisionHandlerQueue,
    CollisionNode,
    CollisionSphere,
    CollisionTraverser,
    NodePath,
    Point3,
)

logger = logging.getLogger(__name__)

# Collision Bitmasks
MASK_WALL = BitMask32.bit(0)         # 0x01: Walls, facades, columns
MASK_OBSTACLE = BitMask32.bit(1)     # 0x02: Furniture, planters, barriers
MASK_VEHICLE = BitMask32.bit(2)      # 0x04: Vehicle bodies
MASK_INTERACTION = BitMask32.bit(3)  # 0x08: Vehicle and kiosk interaction proximity triggers
MASK_CAMERA = BitMask32.bit(4)       # 0x10: Camera occlusion rays


class CollisionWorld:
    """Manages collision solids, pushers, traversers, and interaction proximity volumes."""

    def __init__(self, render: NodePath) -> None:
        self.render = render
        self.root = render.attachNewNode("collision_root")
        self.traverser = CollisionTraverser("main_traverser")
        self.pusher = CollisionHandlerPusher()
        self.interaction_queue = CollisionHandlerQueue()
        self.camera_queue = CollisionHandlerQueue()

        self._triggers: dict[str, NodePath] = {}

    def setup_environment_collisions(self) -> None:
        """Constructs solid collision barriers for all architectural features."""
        # 1. Outer perimeter bounding walls (-27.5 to 27.5)
        # Left wall (glass facade)
        self._add_box_obstacle("col_wall_left", -28.2, 0.0, 4.5, 0.5, 29.0, 4.5)
        # Right wall
        self._add_box_obstacle("col_wall_right", 28.2, 0.0, 4.5, 0.5, 29.0, 4.5)
        # Rear wall
        self._add_box_obstacle("col_wall_rear", 0.0, 28.2, 4.5, 29.0, 0.5, 4.5)
        # Front wall
        self._add_box_obstacle("col_wall_front", 0.0, -28.2, 4.5, 29.0, 0.5, 4.5)

        # 2. Architectural Columns
        col_positions = [
            (-20.0, -16.0), (-20.0, 0.0), (-20.0, 16.0),
            (-6.0, -16.0),  (-6.0, 16.0),
            (6.0, -16.0),   (6.0, 16.0),
            (16.0, -16.0),  (16.0, 0.0),  (16.0, 16.0),
        ]
        for i, (cx, cy) in enumerate(col_positions):
            self._add_box_obstacle(f"col_column_{i}", cx, cy, 4.5, 0.5, 0.5, 4.5)

        # 3. Lounge Furniture (Sofa & Table)
        self._add_box_obstacle("col_sofa_1", 20.0, 14.0, 0.45, 2.1, 0.7, 0.45)
        self._add_box_obstacle("col_sofa_2", 22.6, 12.0, 0.45, 0.7, 1.6, 0.45)
        self._add_box_obstacle("col_table", 20.0, 12.0, 0.25, 1.2, 0.7, 0.25)

        # 4. Planters
        planter_positions = [
            (-18.0, 14.0), (-18.0, -12.0),
            (4.0, 18.0),   (-4.0, 18.0),
            (14.0, 18.0),  (24.0, 6.0),
            (-26.0, 18.0), (-26.0, -18.0),
        ]
        for i, (px, py) in enumerate(planter_positions):
            self._add_box_obstacle(f"col_planter_{i}", px, py, 0.5, 0.55, 0.55, 0.5)

    def _add_box_obstacle(
        self,
        name: str,
        cx: float,
        cy: float,
        cz: float,
        hx: float,
        hy: float,
        hz: float,
    ) -> NodePath:
        """Adds a static box obstacle collider with wall and obstacle masks."""
        c_node = CollisionNode(name)
        c_box = CollisionBox(Point3(0, 0, 0), hx, hy, hz)
        c_node.addSolid(c_box)
        c_node.setIntoCollideMask(MASK_WALL | MASK_OBSTACLE | MASK_CAMERA)
        c_node.setFromCollideMask(BitMask32.allOff())

        np = self.root.attachNewNode(c_node)
        np.setPos(cx, cy, cz)
        return np

    def register_vehicle_obstacle(self, vehicle_id: str, pos: tuple[float, float, float], radius: float = 2.4) -> NodePath:
        """Adds a vehicle solid collider and an interaction proximity trigger."""
        # Solid vehicle obstacle
        c_node = CollisionNode(f"col_veh_{vehicle_id}")
        c_box = CollisionBox(Point3(0, 0, 0.7), 1.2, 2.4, 0.7)
        c_node.addSolid(c_box)
        c_node.setIntoCollideMask(MASK_VEHICLE | MASK_OBSTACLE | MASK_CAMERA)
        c_node.setFromCollideMask(BitMask32.allOff())

        veh_np = self.root.attachNewNode(c_node)
        veh_np.setPos(pos[0], pos[1], pos[2])

        # Interaction trigger zone (sphere around vehicle)
        t_node = CollisionNode(f"trigger_veh_{vehicle_id}")
        t_sphere = CollisionSphere(Point3(0, 0, 0.5), radius)
        t_node.addSolid(t_sphere)
        t_node.setIntoCollideMask(MASK_INTERACTION)
        t_node.setFromCollideMask(BitMask32.allOff())

        t_np = self.root.attachNewNode(t_node)
        t_np.setPos(pos[0], pos[1], pos[2])
        self._triggers[vehicle_id] = t_np
        return veh_np

    def register_player_collider(self, player_np: NodePath, radius: float = 0.45, height: float = 1.7) -> NodePath:
        """Creates player character collider and links to pusher handler."""
        c_node = CollisionNode("player_col")
        # Capsule from z=0.45 to z=height-0.45
        capsule = CollisionCapsule(Point3(0, 0, radius), Point3(0, 0, height - radius), radius)
        c_node.addSolid(capsule)
        c_node.setFromCollideMask(MASK_WALL | MASK_OBSTACLE | MASK_VEHICLE)
        c_node.setIntoCollideMask(BitMask32.allOff())

        col_np = player_np.attachNewNode(c_node)
        self.pusher.addCollider(col_np, player_np)
        self.traverser.addCollider(col_np, self.pusher)
        return col_np

    def register_player_interaction_probe(self, player_np: NodePath) -> NodePath:
        """Probes for nearby vehicle/kiosk interaction trigger volumes."""
        p_node = CollisionNode("player_probe")
        sphere = CollisionSphere(Point3(0, 0, 0.8), 2.8)
        p_node.addSolid(sphere)
        p_node.setFromCollideMask(MASK_INTERACTION)
        p_node.setIntoCollideMask(BitMask32.allOff())

        probe_np = player_np.attachNewNode(p_node)
        self.traverser.addCollider(probe_np, self.interaction_queue)
        return probe_np

    def get_probed_interactive_object(self) -> str | None:
        """Returns the ID of the nearest interactive vehicle/trigger if probed."""
        if self.interaction_queue.getNumEntries() == 0:
            return None

        self.interaction_queue.sortEntries()
        entry = self.interaction_queue.getEntry(0)
        into_node = entry.getIntoNode()
        name = into_node.getName()
        if name.startswith("trigger_veh_"):
            return name[len("trigger_veh_"):]
        return None
