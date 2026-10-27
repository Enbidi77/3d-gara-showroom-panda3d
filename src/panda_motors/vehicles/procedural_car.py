"""Procedural vehicle geometry generator for fallback or custom displays."""

import math

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    Vec3,
    Vec4,
)


def create_procedural_car(name: str = "procedural_car", primary_color: Vec4 = Vec4(0.85, 0.1, 0.15, 1.0)) -> NodePath:
    """Creates a sleek, multi-part procedural sports car model."""
    root = NodePath(name)

    vformat = GeomVertexFormat.getV3n3c4t2()
    vdata = GeomVertexData("car_mesh", vformat, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    color = GeomVertexWriter(vdata, "color")
    texcoord = GeomVertexWriter(vdata, "texcoord")

    tris = GeomTriangles(Geom.UHStatic)

    def add_quad(p1, p2, p3, p4, n, col):
        idx = vertex.getWriteRow()
        for p in (p1, p2, p3, p4):
            vertex.addData3(p)
            normal.addData3(n)
            color.addData4(col)
        texcoord.addData2(0, 0)
        texcoord.addData2(1, 0)
        texcoord.addData2(1, 1)
        texcoord.addData2(0, 1)

        tris.addVertices(idx, idx + 1, idx + 2)
        tris.addVertices(idx, idx + 2, idx + 3)

    c_body = primary_color
    c_glass = Vec4(0.1, 0.15, 0.25, 0.8)
    c_dark = Vec4(0.12, 0.12, 0.14, 1.0)
    c_headlight = Vec4(0.9, 0.95, 1.0, 1.0)
    c_taillight = Vec4(0.9, 0.05, 0.05, 1.0)

    # 1. Main lower chassis / body
    # Nose: y=2.2 to y=1.2, width 1.9, height 0.25 to 0.65
    # Hood: y=1.2 to y=0.5, height 0.65 to 0.75
    # Cabin base: y=0.5 to -1.0, height 0.75
    # Rear deck: y=-1.0 to -2.2, height 0.75 down to 0.65

    # Hood top
    add_quad(
        Vec3(-0.9, 0.5, 0.75), Vec3(0.9, 0.5, 0.75),
        Vec3(0.8, 1.8, 0.60), Vec3(-0.8, 1.8, 0.60),
        Vec3(0, 0.2, 0.98), c_body
    )
    # Nose front wedge
    add_quad(
        Vec3(-0.8, 1.8, 0.60), Vec3(0.8, 1.8, 0.60),
        Vec3(0.75, 2.2, 0.35), Vec3(-0.75, 2.2, 0.35),
        Vec3(0, 0.6, 0.8), c_body
    )
    # Front bumper lower
    add_quad(
        Vec3(-0.75, 2.2, 0.35), Vec3(0.75, 2.2, 0.35),
        Vec3(0.75, 2.15, 0.10), Vec3(-0.75, 2.15, 0.10),
        Vec3(0, 1, 0), c_dark
    )

    # Cabin Roof
    add_quad(
        Vec3(-0.65, -0.6, 1.25), Vec3(0.65, -0.6, 1.25),
        Vec3(0.65, 0.2, 1.25), Vec3(-0.65, 0.2, 1.25),
        Vec3(0, 0, 1), c_body
    )
    # Windshield (slanted forward)
    add_quad(
        Vec3(-0.8, 0.5, 0.75), Vec3(0.8, 0.5, 0.75),
        Vec3(0.65, 0.2, 1.25), Vec3(-0.65, 0.2, 1.25),
        Vec3(0, 0.8, 0.6), c_glass
    )
    # Rear glass (slanted backward fastback)
    add_quad(
        Vec3(-0.65, -0.6, 1.25), Vec3(0.65, -0.6, 1.25),
        Vec3(0.8, -1.5, 0.75), Vec3(-0.8, -1.5, 0.75),
        Vec3(0, -0.8, 0.6), c_glass
    )

    # Cabin Side Windows (Left & Right)
    add_quad(
        Vec3(-0.8, 0.5, 0.75), Vec3(-0.65, 0.2, 1.25),
        Vec3(-0.65, -0.6, 1.25), Vec3(-0.8, -1.4, 0.75),
        Vec3(-1, 0, 0.2), c_glass
    )
    add_quad(
        Vec3(0.8, -1.4, 0.75), Vec3(0.65, -0.6, 1.25),
        Vec3(0.65, 0.2, 1.25), Vec3(0.8, 0.5, 0.75),
        Vec3(1, 0, 0.2), c_glass
    )

    # Rear Deck & Spoiler
    add_quad(
        Vec3(-0.85, -1.5, 0.75), Vec3(0.85, -1.5, 0.75),
        Vec3(0.85, -2.2, 0.70), Vec3(-0.85, -2.2, 0.70),
        Vec3(0, 0, 1), c_body
    )
    # Rear Bumper
    add_quad(
        Vec3(-0.85, -2.2, 0.70), Vec3(0.85, -2.2, 0.70),
        Vec3(0.8, -2.2, 0.15), Vec3(-0.8, -2.2, 0.15),
        Vec3(0, -1, 0), c_body
    )

    # Left & Right Body Sides
    add_quad(
        Vec3(-0.95, 1.8, 0.35), Vec3(-0.95, -2.1, 0.35),
        Vec3(-0.85, -2.1, 0.70), Vec3(-0.85, 1.8, 0.60),
        Vec3(-1, 0, 0), c_body
    )
    add_quad(
        Vec3(0.85, 1.8, 0.60), Vec3(0.85, -2.1, 0.70),
        Vec3(0.95, -2.1, 0.35), Vec3(0.95, 1.8, 0.35),
        Vec3(1, 0, 0), c_body
    )

    # Headlights
    add_quad(
        Vec3(-0.7, 2.05, 0.45), Vec3(-0.45, 2.12, 0.42),
        Vec3(-0.42, 2.0, 0.55), Vec3(-0.68, 1.95, 0.58),
        Vec3(0, 0.8, 0.4), c_headlight
    )
    add_quad(
        Vec3(0.45, 2.12, 0.42), Vec3(0.7, 2.05, 0.45),
        Vec3(0.68, 1.95, 0.58), Vec3(0.42, 2.0, 0.55),
        Vec3(0, 0.8, 0.4), c_headlight
    )

    # Tail lamps
    add_quad(
        Vec3(-0.8, -2.21, 0.55), Vec3(-0.3, -2.21, 0.55),
        Vec3(-0.3, -2.21, 0.63), Vec3(-0.8, -2.21, 0.63),
        Vec3(0, -1, 0), c_taillight
    )
    add_quad(
        Vec3(0.3, -2.21, 0.55), Vec3(0.8, -2.21, 0.55),
        Vec3(0.8, -2.21, 0.63), Vec3(0.3, -2.21, 0.63),
        Vec3(0, -1, 0), c_taillight
    )

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    geom_node = GeomNode("car_body_geom")
    geom_node.addGeom(geom)
    root.attachNewNode(geom_node)

    # Add wheels
    wheel_positions = [
        (-0.95, 1.35, 0.33),
        (0.95, 1.35, 0.33),
        (-0.95, -1.35, 0.35),
        (0.95, -1.35, 0.35),
    ]

    for i, (wx, wy, wz) in enumerate(wheel_positions):
        wheel = _create_wheel_node(f"wheel_{i}", radius=0.34, width=0.22)
        wheel.reparentTo(root)
        wheel.setPos(wx, wy, wz)

    return root


def _create_wheel_node(name: str, radius: float = 0.34, width: float = 0.22, segments: int = 16) -> NodePath:
    """Builds a 3D cylindrical wheel with rim and tire."""
    node = NodePath(name)
    vformat = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData("wheel_mesh", vformat, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    color = GeomVertexWriter(vdata, "color")
    tris = GeomTriangles(Geom.UHStatic)

    c_tire = Vec4(0.08, 0.08, 0.08, 1.0)
    c_rim = Vec4(0.85, 0.87, 0.90, 1.0)

    half_w = width * 0.5
    angles = [i * 2.0 * math.pi / segments for i in range(segments + 1)]

    # Tire tread cylinder
    for i in range(segments):
        a1, a2 = angles[i], angles[i + 1]
        y1, z1 = math.cos(a1) * radius, math.sin(a1) * radius
        y2, z2 = math.cos(a2) * radius, math.sin(a2) * radius

        idx = vertex.getWriteRow()
        for x, y, z in [(-half_w, y1, z1), (half_w, y1, z1), (half_w, y2, z2), (-half_w, y2, z2)]:
            vertex.addData3(x, y, z)
            norm = Vec3(0, y, z).normalized()
            normal.addData3(norm)
            color.addData4(c_tire)

        tris.addVertices(idx, idx + 1, idx + 2)
        tris.addVertices(idx, idx + 2, idx + 3)

    # Rim caps (outer and inner)
    for sign in [-1.0, 1.0]:
        x = sign * half_w
        norm_x = sign
        center_idx = vertex.getWriteRow()
        vertex.addData3(x, 0, 0)
        normal.addData3(norm_x, 0, 0)
        color.addData4(c_rim if sign > 0 else c_tire)

        for i in range(segments):
            a = angles[i]
            y, z = math.cos(a) * (radius * 0.7 if sign > 0 else radius), math.sin(a) * (radius * 0.7 if sign > 0 else radius)
            vertex.addData3(x, y, z)
            normal.addData3(norm_x, 0, 0)
            color.addData4(c_rim if sign > 0 else c_tire)

        for i in range(segments):
            p1 = center_idx + 1 + i
            p2 = center_idx + 1 + ((i + 1) % segments)
            if sign > 0:
                tris.addVertices(center_idx, p1, p2)
            else:
                tris.addVertices(center_idx, p2, p1)

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    geom_node = GeomNode(f"{name}_geom")
    geom_node.addGeom(geom)
    node.attachNewNode(geom_node)
    return node
