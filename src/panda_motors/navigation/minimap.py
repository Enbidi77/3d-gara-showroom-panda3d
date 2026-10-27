"""Minimap radar HUD widget displaying showroom floor plan and player position."""

import math

from direct.gui.DirectGui import OnscreenText
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    Point3,
    TextNode,
    TransparencyAttrib,
    Vec4,
)

from panda_motors.navigation.player_controller import PlayerController

WORLD_RADIUS = 30.0  # Max showroom extent mapped to radar


class MinimapHUD:
    """Circular radar floor plan displaying player location, platform blips, and compass directions."""

    def __init__(self, parent_2d: NodePath, player_controller: PlayerController) -> None:
        self.player_controller = player_controller

        # Positioned at bottom-left: x=-1.45, z=-0.65 in aspect2d
        self.root = parent_2d.attachNewNode("minimap_hud")
        self.root.setPos(-1.38, 0, -0.62)

        self.radar_radius = 0.26  # Screen units in aspect2d
        self._build_radar_background()
        self._build_compass_labels()
        self._build_platform_blips()
        self._build_player_marker()

    def _build_radar_background(self) -> None:
        """Constructs circular translucent glass radar frame."""
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData("radar_mesh", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)

        segments = 40
        c_bg = Vec4(0.06, 0.08, 0.12, 0.85)
        c_ring = Vec4(0.2, 0.55, 0.85, 0.9)

        # Center vertex
        center_idx = vertex.getWriteRow()
        vertex.addData3(0, 0, 0); normal.addData3(0, 0, 1); color.addData4(c_bg)

        angles = [i * 2.0 * math.pi / segments for i in range(segments + 1)]
        start_idx = vertex.getWriteRow()
        for a in angles[:-1]:
            px = math.cos(a) * self.radar_radius
            pz = math.sin(a) * self.radar_radius
            vertex.addData3(px, 0, pz); normal.addData3(0, 0, 1); color.addData4(c_bg)

        for i in range(segments):
            tris.addVertices(center_idx, start_idx + i, start_idx + ((i + 1) % segments))

        # Outer border ring
        r_outer = self.radar_radius + 0.012
        r_inner = self.radar_radius - 0.004
        for i in range(segments):
            a1, a2 = angles[i], angles[i + 1]
            p1 = Point3(math.cos(a1) * r_inner, 0, math.sin(a1) * r_inner)
            p2 = Point3(math.cos(a2) * r_inner, 0, math.sin(a2) * r_inner)
            p3 = Point3(math.cos(a2) * r_outer, 0, math.sin(a2) * r_outer)
            p4 = Point3(math.cos(a1) * r_outer, 0, math.sin(a1) * r_outer)

            idx = vertex.getWriteRow()
            for p in (p1, p2, p3, p4):
                vertex.addData3(p); normal.addData3(0, 0, 1); color.addData4(c_ring)
            tris.addVertices(idx, idx + 1, idx + 2)
            tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode("radar_geom")
        gnode.addGeom(geom)

        np = self.root.attachNewNode(gnode)
        np.setTransparency(TransparencyAttrib.M_alpha)

    def _build_compass_labels(self) -> None:
        """Adds N, S, E, W compass direction labels around radar."""
        offset = self.radar_radius + 0.028
        compass = [
            ("N", 0, offset),
            ("S", 0, -offset),
            ("E", offset, 0),
            ("W", -offset, 0),
        ]
        for text, x, z in compass:
            OnscreenText(
                text=text,
                parent=self.root,
                pos=(x, z - 0.015),
                scale=0.035,
                fg=(0.7, 0.8, 0.95, 0.9),
                align=TextNode.ACenter,
                mayChange=False,
            )

    def _build_platform_blips(self) -> None:
        """Draws circles representing the vehicle platforms on the radar."""
        self.blips_node = self.root.attachNewNode("blips_node")
        platforms = [
            (0.0, 0.0, 4.8),
            (12.0, 10.0, 4.2),
            (-12.0, 8.0, 4.2),
            (14.0, -4.0, 4.2),
            (20.0, 4.0, 4.0),
            (-14.0, -4.0, 4.2),
        ]

        for px, py, r in platforms:
            # Map world coords to radar coords
            rx = (px / WORLD_RADIUS) * (self.radar_radius * 0.85)
            rz = (py / WORLD_RADIUS) * (self.radar_radius * 0.85)
            dot = self._create_dot(radius=0.016, color=Vec4(0.2, 0.65, 1.0, 0.85))
            dot.reparentTo(self.blips_node)
            dot.setPos(rx, 0, rz)

    def _create_dot(self, radius: float = 0.015, color: Vec4 = Vec4(0.2, 0.6, 1.0, 1.0)) -> NodePath:
        """Creates a small 2D disc dot."""
        node = NodePath("dot")
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData("dot_mesh", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        cwriter = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)

        c_idx = vertex.getWriteRow()
        vertex.addData3(0, 0, 0); normal.addData3(0, 0, 1); cwriter.addData4(color)
        segs = 16
        for i in range(segs):
            a = i * 2.0 * math.pi / segs
            vertex.addData3(math.cos(a) * radius, 0, math.sin(a) * radius)
            normal.addData3(0, 0, 1); cwriter.addData4(color)

        for i in range(segs):
            tris.addVertices(c_idx, c_idx + 1 + i, c_idx + 1 + ((i + 1) % segs))

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode("dot_geom")
        gnode.addGeom(geom)
        np = node.attachNewNode(gnode)
        np.setTransparency(TransparencyAttrib.M_alpha)
        return node

    def _build_player_marker(self) -> None:
        """Constructs an aerodynamic chevron arrow for the player indicator."""
        self.player_marker = self.root.attachNewNode("player_marker")

        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData("arrow_mesh", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)

        c_arrow = Vec4(0.0, 0.85, 1.0, 1.0)
        # Upward pointing triangle
        p_tip = Point3(0, 0, 0.028)
        p_left = Point3(-0.016, 0, -0.018)
        p_notch = Point3(0, 0, -0.008)
        p_right = Point3(0.016, 0, -0.018)

        for p in (p_tip, p_left, p_notch, p_right):
            vertex.addData3(p); normal.addData3(0, 0, 1); color.addData4(c_arrow)

        # Left wing
        tris.addVertices(0, 1, 2)
        # Right wing
        tris.addVertices(0, 2, 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode("arrow_geom")
        gnode.addGeom(geom)
        arrow_np = self.player_marker.attachNewNode(gnode)
        arrow_np.setTransparency(TransparencyAttrib.M_alpha)

    def update(self) -> None:
        """Updates player marker position and rotation on the radar."""
        pos = self.player_controller.position
        rx = (pos.getX() / WORLD_RADIUS) * (self.radar_radius * 0.85)
        rz = (pos.getY() / WORLD_RADIUS) * (self.radar_radius * 0.85)

        # Clamp to radar disc boundary
        dist = math.hypot(rx, rz)
        max_d = self.radar_radius * 0.88
        if dist > max_d:
            rx = (rx / dist) * max_d
            rz = (rz / dist) * max_d

        self.player_marker.setPos(rx, 0, rz)
        # Player heading in Panda3D: 0 degrees is facing +Y (North)
        # Roll in 2D plane: setR(-heading)
        self.player_marker.setR(-self.player_controller.yaw)

    def hide(self) -> None:
        self.root.hide()

    def show(self) -> None:
        self.root.show()
