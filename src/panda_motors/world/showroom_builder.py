"""Showroom architecture, structural geometry, lighting, and environmental props."""

import logging
import math

from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    Material,
    NodePath,
    PerspectiveLens,
    Point3,
    SamplerState,
    Spotlight,
    TexGenAttrib,
    TextureStage,
    TransparencyAttrib,
    Vec3,
    Vec4,
)

from panda_motors.core.asset_manager import AssetManager

logger = logging.getLogger(__name__)


class ShowroomBuilder:
    """Constructs the high-end 3D architectural showroom environment."""

    def __init__(self, render: NodePath, asset_manager: AssetManager) -> None:
        self.render = render
        self.asset_manager = asset_manager
        self.root = NodePath("showroom_root")
        self.root.reparentTo(render)

        # Architectural group nodes
        self.structure_node = self.root.attachNewNode("structure")
        self.platforms_node = self.root.attachNewNode("platforms")
        self.lighting_node = self.root.attachNewNode("lighting")
        self.furniture_node = self.root.attachNewNode("furniture")
        self.props_node = self.root.attachNewNode("props")
        self.kiosks_node = self.root.attachNewNode("kiosks")

        self.platform_transforms: list[tuple[float, float, float, float]] = []

    def build_all(self) -> NodePath:
        """Assembles the complete showroom environment."""
        self._build_floor()
        self._build_walls_and_facade()
        self._build_panoramic_skyline()
        self._build_ceiling_and_roof()
        self._build_feature_wall()
        self._build_mezzanine()
        self._build_platforms()
        self._build_columns()
        self._build_customer_lounge()
        self._build_planters_and_plants()
        self._build_spec_kiosks()
        self._setup_lighting()
        return self.root

    def _build_floor(self) -> None:
        """Constructs the polished reflective marble floor."""
        vformat = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData("floor_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        tris = GeomTriangles(Geom.UHStatic)

        size = 35.0  # -35 to +35 in X and Y
        tile_repeat = 12.0

        p1 = Point3(-size, -size, 0.0)
        p2 = Point3(size, -size, 0.0)
        p3 = Point3(size, size, 0.0)
        p4 = Point3(-size, size, 0.0)
        norm = Vec3(0, 0, 1)

        idx = vertex.getWriteRow()
        vertex.addData3(p1); normal.addData3(norm); color.addData4(Vec4(0.95, 0.95, 0.97, 1.0)); texcoord.addData2(0, 0)
        vertex.addData3(p2); normal.addData3(norm); color.addData4(Vec4(0.95, 0.95, 0.97, 1.0)); texcoord.addData2(tile_repeat, 0)
        vertex.addData3(p3); normal.addData3(norm); color.addData4(Vec4(0.95, 0.95, 0.97, 1.0)); texcoord.addData2(tile_repeat, tile_repeat)
        vertex.addData3(p4); normal.addData3(norm); color.addData4(Vec4(0.95, 0.95, 0.97, 1.0)); texcoord.addData2(0, tile_repeat)

        tris.addVertices(idx, idx + 1, idx + 2)
        tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode("floor_geom")
        gnode.addGeom(geom)
        floor_np = self.structure_node.attachNewNode(gnode)

        # Marble texture & material
        marble_tex = self.asset_manager.load_texture("assets/textures/marble/marble_01_diff_1k.jpg")
        if marble_tex:
            marble_tex.setWrapU(SamplerState.WM_repeat)
            marble_tex.setWrapV(SamplerState.WM_repeat)
            floor_np.setTexture(marble_tex)

        rough_tex = self.asset_manager.load_texture("assets/textures/marble/marble_01_rough_1k.jpg")
        if rough_tex:
            rough_tex.setWrapU(SamplerState.WM_repeat)
            rough_tex.setWrapV(SamplerState.WM_repeat)

        mat = Material("marble_floor_mat")
        mat.setDiffuse(Vec4(0.95, 0.95, 0.97, 1.0))
        mat.setSpecular(Vec4(0.9, 0.92, 0.98, 1.0))
        mat.setShininess(95.0)
        mat.setRoughness(0.08)
        mat.setMetallic(0.12)
        floor_np.setMaterial(mat)

        # Environment reflection sphere-map effect for marble gloss
        env_tex = self.asset_manager.load_texture("assets/textures/env/royal_esplanade.jpg")
        if env_tex:
            ts = TextureStage("floor_env")
            ts.setMode(TextureStage.M_blend)
            ts.setColor(Vec4(1, 1, 1, 0.22))
            floor_np.setTexture(ts, env_tex)
            floor_np.setTexGen(ts, TexGenAttrib.M_eye_sphere_map)

    def _build_walls_and_facade(self) -> None:
        """Constructs exterior perimeter walls and the monumental panoramic glass facade."""
        # 1. Left Panoramic Window Facade (X = -28.0, Y = -28 to +28, Z = 0 to 9.0)
        # Transparent glass panels
        glass_np = self._create_quad(
            Point3(-28.0, 28.0, 9.0),
            Point3(-28.0, -28.0, 9.0),
            Point3(-28.0, -28.0, 0.1),
            Point3(-28.0, 28.0, 0.1),
            Vec3(1, 0, 0),
            Vec4(0.65, 0.85, 0.95, 0.18),
            name="panoramic_glass",
        )
        glass_np.reparentTo(self.structure_node)
        glass_np.setTransparency(TransparencyAttrib.M_alpha)
        glass_np.setTwoSided(True)

        glass_mat = Material("panoramic_glass_mat")
        glass_mat.setDiffuse(Vec4(0.8, 0.9, 1.0, 0.15))
        glass_mat.setSpecular(Vec4(1.0, 1.0, 1.0, 1.0))
        glass_mat.setShininess(120.0)
        glass_mat.setRoughness(0.02)
        glass_np.setMaterial(glass_mat)

        # Aluminum mullions (window framing posts every 4 meters)
        mullion_mat = Material("mullion_mat")
        mullion_mat.setDiffuse(Vec4(0.15, 0.15, 0.17, 1.0))
        mullion_mat.setMetallic(0.8)
        mullion_mat.setRoughness(0.3)

        for y in range(-28, 29, 4):
            post = self._create_box(
                name=f"mullion_{y}",
                dx=0.15, dy=0.15, dz=9.0,
                color=Vec4(0.15, 0.15, 0.17, 1.0),
            )
            post.reparentTo(self.structure_node)
            post.setPos(-28.0, y, 4.5)
            post.setMaterial(mullion_mat)

        # Horizontal mullion rails at z=3.0, z=6.0, z=9.0
        for z in [3.0, 6.0, 9.0]:
            rail = self._create_box(
                name=f"mullion_rail_{z}",
                dx=0.12, dy=56.0, dz=0.12,
                color=Vec4(0.15, 0.15, 0.17, 1.0),
            )
            rail.reparentTo(self.structure_node)
            rail.setPos(-28.0, 0.0, z)
            rail.setMaterial(mullion_mat)

        # 2. Right solid wall (X = +28.0, Y = -28 to +28, Z = 0 to 9.0)
        right_wall = self._create_quad(
            Point3(28.0, -28.0, 9.0),
            Point3(28.0, 28.0, 9.0),
            Point3(28.0, 28.0, 0.0),
            Point3(28.0, -28.0, 0.0),
            Vec3(-1, 0, 0),
            Vec4(0.90, 0.91, 0.93, 1.0),
            name="right_wall",
        )
        right_wall.reparentTo(self.structure_node)

        # 3. Front wall with Entrance Foyer (Y = -28.0, X = -28 to +28, Z = 0 to 9.0)
        front_left = self._create_quad(
            Point3(-28.0, -28.0, 9.0),
            Point3(-6.0, -28.0, 9.0),
            Point3(-6.0, -28.0, 0.0),
            Point3(-28.0, -28.0, 0.0),
            Vec3(0, 1, 0),
            Vec4(0.92, 0.93, 0.95, 1.0),
            name="front_wall_left",
        )
        front_left.reparentTo(self.structure_node)

        front_right = self._create_quad(
            Point3(6.0, -28.0, 9.0),
            Point3(28.0, -28.0, 9.0),
            Point3(28.0, -28.0, 0.0),
            Point3(6.0, -28.0, 0.0),
            Vec3(0, 1, 0),
            Vec4(0.92, 0.93, 0.95, 1.0),
            name="front_wall_right",
        )
        front_right.reparentTo(self.structure_node)

        # Front Glass Entrance portal in center
        front_glass = self._create_quad(
            Point3(-6.0, -28.0, 9.0),
            Point3(6.0, -28.0, 9.0),
            Point3(6.0, -28.0, 0.0),
            Point3(-6.0, -28.0, 0.0),
            Vec3(0, 1, 0),
            Vec4(0.65, 0.85, 0.95, 0.25),
            name="front_glass_portal",
        )
        front_glass.reparentTo(self.structure_node)
        front_glass.setTransparency(TransparencyAttrib.M_alpha)
        front_glass.setTwoSided(True)

    def _build_panoramic_skyline(self) -> None:
        """Builds the outdoor panoramic vista visible through the left glass facade."""
        # Curved backdrop cylinder placed outside the window at X = -38 to -44
        pano_node = NodePath("panoramic_skyline")
        pano_node.reparentTo(self.structure_node)

        vformat = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData("pano_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        tris = GeomTriangles(Geom.UHStatic)

        # Build cylindrical arc outside the window
        segments = 36
        radius = 52.0
        angle_start = math.pi * 0.75
        angle_end = math.pi * 1.25
        height_bottom = -4.0
        height_top = 28.0

        for i in range(segments):
            f1 = i / segments
            f2 = (i + 1) / segments
            a1 = angle_start + f1 * (angle_end - angle_start)
            a2 = angle_start + f2 * (angle_end - angle_start)

            x1, y1 = math.cos(a1) * radius, math.sin(a1) * radius
            x2, y2 = math.cos(a2) * radius, math.sin(a2) * radius

            idx = vertex.getWriteRow()
            norm = Vec3(x1, y1, 0).normalized()

            vertex.addData3(x1, y1, height_bottom); normal.addData3(norm); color.addData4(Vec4(1, 1, 1, 1)); texcoord.addData2(f1, 0)
            vertex.addData3(x2, y2, height_bottom); normal.addData3(norm); color.addData4(Vec4(1, 1, 1, 1)); texcoord.addData2(f2, 0)
            vertex.addData3(x2, y2, height_top); normal.addData3(norm); color.addData4(Vec4(1, 1, 1, 1)); texcoord.addData2(f2, 1)
            vertex.addData3(x1, y1, height_top); normal.addData3(norm); color.addData4(Vec4(1, 1, 1, 1)); texcoord.addData2(f1, 1)

            tris.addVertices(idx, idx + 2, idx + 1)
            tris.addVertices(idx, idx + 3, idx + 2)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode("pano_geom")
        gnode.addGeom(geom)
        pano_np = pano_node.attachNewNode(gnode)
        pano_np.setLightOff()

        # Load skyline panorama texture
        sky_tex = self.asset_manager.load_texture("assets/textures/env/skyline_panorama.jpg")
        if sky_tex:
            sky_tex.setWrapU(SamplerState.WM_clamp)
            sky_tex.setWrapV(SamplerState.WM_clamp)
            pano_np.setTexture(sky_tex)

        # Outdoor blue water plane between window and panorama
        water = self._create_quad(
            Point3(-28.0, 40.0, -0.05),
            Point3(-60.0, 40.0, -0.05),
            Point3(-60.0, -40.0, -0.05),
            Point3(-28.0, -40.0, -0.05),
            Vec3(0, 0, 1),
            Vec4(0.2, 0.45, 0.70, 1.0),
            name="outdoor_water",
        )
        water.reparentTo(pano_node)
        water_mat = Material("water_mat")
        water_mat.setDiffuse(Vec4(0.18, 0.45, 0.75, 1.0))
        water_mat.setSpecular(Vec4(0.9, 0.95, 1.0, 1.0))
        water_mat.setShininess(100.0)
        water.setMaterial(water_mat)

    def _build_ceiling_and_roof(self) -> None:
        """Constructs the high architectural ceiling with dark panels and recessed lights."""
        # Main ceiling slab at Z = 9.0m
        ceiling = self._create_quad(
            Point3(-28.0, -28.0, 9.0),
            Point3(28.0, -28.0, 9.0),
            Point3(28.0, 28.0, 9.0),
            Point3(-28.0, 28.0, 9.0),
            Vec3(0, 0, -1),
            Vec4(0.16, 0.17, 0.19, 1.0),
            name="ceiling_main",
        )
        ceiling.reparentTo(self.structure_node)

        # Recessed longitudinal lighting troughs
        light_trough_mat = Material("light_trough_mat")
        light_trough_mat.setEmission(Vec4(0.95, 0.97, 1.0, 1.0))

        for x in [-14.0, 0.0, 14.0]:
            strip = self._create_quad(
                Point3(x - 0.4, -25.0, 8.95),
                Point3(x + 0.4, -25.0, 8.95),
                Point3(x + 0.4, 25.0, 8.95),
                Point3(x - 0.4, 25.0, 8.95),
                Vec3(0, 0, -1),
                Vec4(1.0, 1.0, 1.0, 1.0),
                name=f"ceiling_light_strip_{x}",
            )
            strip.reparentTo(self.structure_node)
            strip.setLightOff()
            strip.setMaterial(light_trough_mat)

    def _build_feature_wall(self) -> None:
        """Constructs the dramatic central feature wall with glowing Panda Motors logo."""
        # Rear Feature Wall at Y = 28.0
        # Center section: Dark textured charcoal acoustic panel
        wall = self._create_quad(
            Point3(-12.0, 27.9, 9.0),
            Point3(12.0, 27.9, 9.0),
            Point3(12.0, 27.9, 0.0),
            Point3(-12.0, 27.9, 0.0),
            Vec3(0, -1, 0),
            Vec4(0.12, 0.13, 0.15, 1.0),
            name="center_feature_wall",
        )
        wall.reparentTo(self.structure_node)

        wall_mat = Material("feature_wall_mat")
        wall_mat.setDiffuse(Vec4(0.12, 0.13, 0.15, 1.0))
        wall_mat.setRoughness(0.85)
        wall.setMaterial(wall_mat)

        # Flanking walls left and right
        wall_l = self._create_quad(
            Point3(-28.0, 27.9, 9.0), Point3(-12.0, 27.9, 9.0),
            Point3(-12.0, 27.9, 0.0), Point3(-28.0, 27.9, 0.0),
            Vec3(0, -1, 0), Vec4(0.88, 0.90, 0.92, 1.0), name="wall_rear_left"
        )
        wall_l.reparentTo(self.structure_node)

        wall_r = self._create_quad(
            Point3(12.0, 27.9, 9.0), Point3(28.0, 27.9, 9.0),
            Point3(28.0, 27.9, 0.0), Point3(12.0, 27.9, 0.0),
            Vec3(0, -1, 0), Vec4(0.88, 0.90, 0.92, 1.0), name="wall_rear_right"
        )
        wall_r.reparentTo(self.structure_node)

        # Illuminated Panda Motors Wall Logo Sign
        logo_quad = self._create_quad(
            Point3(-4.0, 27.85, 7.8),
            Point3(4.0, 27.85, 7.8),
            Point3(4.0, 27.85, 3.8),
            Point3(-4.0, 27.85, 3.8),
            Vec3(0, -1, 0),
            Vec4(1, 1, 1, 1),
            name="panda_wall_logo",
        )
        logo_quad.reparentTo(self.structure_node)
        logo_quad.setTransparency(TransparencyAttrib.M_alpha)
        logo_quad.setLightOff()

        logo_tex = self.asset_manager.load_texture("assets/textures/ui/panda_wall_sign.png")
        if logo_tex:
            logo_quad.setTexture(logo_tex)

        # Backlit vertical glow strips on the feature wall
        glow_mat = Material("glow_mat")
        glow_mat.setEmission(Vec4(0.8, 0.9, 1.0, 1.0))
        for x in [-12.0, 12.0]:
            accent = self._create_box(
                name=f"feature_glow_strip_{x}",
                dx=0.1, dy=0.08, dz=8.5,
                color=Vec4(0.85, 0.92, 1.0, 1.0)
            )
            accent.reparentTo(self.structure_node)
            accent.setPos(x, 27.85, 4.25)
            accent.setLightOff()

    def _build_mezzanine(self) -> None:
        """Constructs upper VIP mezzanine level on the right side."""
        # Mezzanine deck at Z = 4.2m, X = 16 to 28, Y = -18 to 22
        mezz = self._create_box(
            name="mezzanine_deck",
            dx=12.0, dy=40.0, dz=0.35,
            color=Vec4(0.18, 0.19, 0.22, 1.0),
        )
        mezz.reparentTo(self.structure_node)
        mezz.setPos(22.0, 2.0, 4.2)

        # Glass balustrade along mezzanine edge (X = 16.0, Y = -18 to 22, Z = 4.38 to 5.48)
        rail_glass = self._create_quad(
            Point3(16.0, -18.0, 5.35),
            Point3(16.0, 22.0, 5.35),
            Point3(16.0, 22.0, 4.38),
            Point3(16.0, -18.0, 4.38),
            Vec3(-1, 0, 0),
            Vec4(0.7, 0.85, 0.95, 0.25),
            name="mezzanine_glass_rail",
        )
        rail_glass.reparentTo(self.structure_node)
        rail_glass.setTransparency(TransparencyAttrib.M_alpha)
        rail_glass.setTwoSided(True)

        # Stainless steel handrail cap on top of glass
        handrail = self._create_box(
            name="mezzanine_handrail",
            dx=0.10, dy=40.0, dz=0.08,
            color=Vec4(0.85, 0.88, 0.92, 1.0),
        )
        handrail.reparentTo(self.structure_node)
        handrail.setPos(16.0, 2.0, 5.39)

    def _build_platforms(self) -> None:
        """Constructs circular raised display platforms with neon perimeter lighting and overhead suspended ring lights."""
        # Platform definitions: (x, y, radius, height, name)
        platforms = [
            (0.0, 0.0, 4.8, 0.18, "centerpiece_rotunda"),
            (12.0, 10.0, 4.2, 0.18, "hypercar_podium"),
            (-12.0, 8.0, 4.2, 0.18, "supercar_podium"),
            (14.0, -4.0, 4.2, 0.18, "suv_podium"),
            (20.0, 4.0, 4.0, 0.18, "gt_podium"),
            (-14.0, -4.0, 4.2, 0.18, "ev_podium"),
        ]

        for x, y, radius, height, name in platforms:
            self.platform_transforms.append((x, y, radius, height))
            p_node = self._create_circular_platform(name, radius=radius, height=height)
            p_node.reparentTo(self.platforms_node)
            p_node.setPos(x, y, 0.0)

            # Suspended ceiling ring light centered directly above each platform
            ring = self._create_suspended_ring_light(f"ring_light_{name}", radius=radius * 0.85)
            ring.reparentTo(self.lighting_node)
            ring.setPos(x, y, 8.2)

    def _create_circular_platform(self, name: str, radius: float = 4.5, height: float = 0.18, segments: int = 40) -> NodePath:
        """Creates a raised circular platform with illuminated LED perimeter ring."""
        root = NodePath(name)

        vformat = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData(f"{name}_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        tris = GeomTriangles(Geom.UHStatic)

        c_top = Vec4(0.92, 0.93, 0.95, 1.0)
        c_rim = Vec4(0.15, 0.16, 0.18, 1.0)
        c_led = Vec4(0.3, 0.75, 1.0, 1.0)

        # Top disc center
        center_idx = vertex.getWriteRow()
        vertex.addData3(0, 0, height)
        normal.addData3(0, 0, 1)
        color.addData4(c_top)
        texcoord.addData2(0.5, 0.5)

        angles = [i * 2.0 * math.pi / segments for i in range(segments + 1)]

        # Top perimeter vertices
        top_start_idx = vertex.getWriteRow()
        for a in angles[:-1]:
            px, py = math.cos(a) * radius, math.sin(a) * radius
            vertex.addData3(px, py, height)
            normal.addData3(0, 0, 1)
            color.addData4(c_top)
            texcoord.addData2(0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a))

        # Disc triangles
        for i in range(segments):
            p1 = top_start_idx + i
            p2 = top_start_idx + ((i + 1) % segments)
            tris.addVertices(center_idx, p1, p2)

        # LED Glowing Ring Bevel (height - 0.04 to height)
        led_bottom = height - 0.04
        for i in range(segments):
            a1, a2 = angles[i], angles[i + 1]
            x1, y1 = math.cos(a1) * (radius + 0.04), math.sin(a1) * (radius + 0.04)
            x2, y2 = math.cos(a2) * (radius + 0.04), math.sin(a2) * (radius + 0.04)
            n1 = Vec3(math.cos(a1), math.sin(a1), 0.3).normalized()
            n2 = Vec3(math.cos(a2), math.sin(a2), 0.3).normalized()

            idx = vertex.getWriteRow()
            vertex.addData3(x1, y1, height); normal.addData3(n1); color.addData4(c_led); texcoord.addData2(0, 1)
            vertex.addData3(x2, y2, height); normal.addData3(n2); color.addData4(c_led); texcoord.addData2(1, 1)
            vertex.addData3(x2, y2, led_bottom); normal.addData3(n2); color.addData4(c_led); texcoord.addData2(1, 0)
            vertex.addData3(x1, y1, led_bottom); normal.addData3(n1); color.addData4(c_led); texcoord.addData2(0, 0)

            tris.addVertices(idx, idx + 1, idx + 2)
            tris.addVertices(idx, idx + 2, idx + 3)

        # Base Cylinder side wall (0 to led_bottom)
        for i in range(segments):
            a1, a2 = angles[i], angles[i + 1]
            x1, y1 = math.cos(a1) * (radius + 0.04), math.sin(a1) * (radius + 0.04)
            x2, y2 = math.cos(a2) * (radius + 0.04), math.sin(a2) * (radius + 0.04)
            n1 = Vec3(math.cos(a1), math.sin(a1), 0).normalized()
            n2 = Vec3(math.cos(a2), math.sin(a2), 0).normalized()

            idx = vertex.getWriteRow()
            vertex.addData3(x1, y1, led_bottom); normal.addData3(n1); color.addData4(c_rim); texcoord.addData2(0, 1)
            vertex.addData3(x2, y2, led_bottom); normal.addData3(n2); color.addData4(c_rim); texcoord.addData2(1, 1)
            vertex.addData3(x2, y2, 0.0); normal.addData3(n2); color.addData4(c_rim); texcoord.addData2(1, 0)
            vertex.addData3(x1, y1, 0.0); normal.addData3(n1); color.addData4(c_rim); texcoord.addData2(0, 0)

            tris.addVertices(idx, idx + 1, idx + 2)
            tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode(f"{name}_geom")
        gnode.addGeom(geom)
        platform_np = root.attachNewNode(gnode)

        # Polished platform material
        mat = Material("platform_mat")
        mat.setDiffuse(Vec4(0.90, 0.91, 0.94, 1.0))
        mat.setSpecular(Vec4(1.0, 1.0, 1.0, 1.0))
        mat.setShininess(110.0)
        mat.setRoughness(0.06)
        mat.setMetallic(0.2)
        platform_np.setMaterial(mat)

        return root

    def _create_suspended_ring_light(self, name: str, radius: float = 3.6, segments: int = 32) -> NodePath:
        """Constructs an elegant glowing LED torus ring suspended from the ceiling."""
        root = NodePath(name)
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData(f"{name}_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)

        c_glow = Vec4(0.95, 0.98, 1.0, 1.0)
        ring_thickness = 0.08
        tube_segments = 8

        angles_ring = [i * 2.0 * math.pi / segments for i in range(segments + 1)]
        angles_tube = [j * 2.0 * math.pi / tube_segments for j in range(tube_segments + 1)]

        for i in range(segments):
            a_ring1 = angles_ring[i]
            a_ring2 = angles_ring[i + 1]

            cx1, cy1 = math.cos(a_ring1) * radius, math.sin(a_ring1) * radius
            cx2, cy2 = math.cos(a_ring2) * radius, math.sin(a_ring2) * radius

            for j in range(tube_segments):
                at1 = angles_tube[j]
                at2 = angles_tube[j + 1]

                def get_pt(cx, cy, a_r, a_t):
                    dir_r = Vec3(math.cos(a_r), math.sin(a_r), 0)
                    off = dir_r * (math.cos(a_t) * ring_thickness) + Vec3(0, 0, math.sin(a_t) * ring_thickness)
                    pt = Point3(cx, cy, 0) + off
                    norm = off.normalized()
                    return pt, norm

                p1, n1 = get_pt(cx1, cy1, a_ring1, at1)
                p2, n2 = get_pt(cx2, cy2, a_ring2, at1)
                p3, n3 = get_pt(cx2, cy2, a_ring2, at2)
                p4, n4 = get_pt(cx1, cy1, a_ring1, at2)

                idx = vertex.getWriteRow()
                for p, n in [(p1, n1), (p2, n2), (p3, n3), (p4, n4)]:
                    vertex.addData3(p); normal.addData3(n); color.addData4(c_glow)

                tris.addVertices(idx, idx + 1, idx + 2)
                tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode(f"{name}_geom")
        gnode.addGeom(geom)
        ring_np = root.attachNewNode(gnode)
        ring_np.setLightOff()

        # Thin suspension cables to ceiling (Z = 0.0 to 0.8 above ring)
        for ca in [0, math.pi * 0.667, math.pi * 1.333]:
            cable = self._create_box(
                name=f"cable_{ca}",
                dx=0.015, dy=0.015, dz=0.8,
                color=Vec4(0.2, 0.2, 0.22, 1.0),
            )
            cable.reparentTo(root)
            cable.setPos(math.cos(ca) * radius, math.sin(ca) * radius, 0.4)

        return root

    def _build_columns(self) -> None:
        """Constructs modern architectural columns supporting the roof."""
        col_positions = [
            (-20.0, -16.0), (-20.0, 0.0), (-20.0, 16.0),
            (-6.0, -16.0),  (-6.0, 16.0),
            (6.0, -16.0),   (6.0, 16.0),
            (16.0, -16.0),  (16.0, 0.0),  (16.0, 16.0),
        ]

        col_mat = Material("column_mat")
        col_mat.setDiffuse(Vec4(0.88, 0.90, 0.92, 1.0))
        col_mat.setMetallic(0.3)
        col_mat.setRoughness(0.2)

        for i, (cx, cy) in enumerate(col_positions):
            col = self._create_box(
                name=f"column_{i}",
                dx=0.7, dy=0.7, dz=9.0,
                color=Vec4(0.88, 0.90, 0.92, 1.0),
            )
            col.reparentTo(self.structure_node)
            col.setPos(cx, cy, 4.5)
            col.setMaterial(col_mat)

            # Polished stainless steel column base collar
            collar = self._create_box(
                name=f"col_collar_{i}",
                dx=0.82, dy=0.82, dz=0.25,
                color=Vec4(0.25, 0.26, 0.28, 1.0),
            )
            collar.reparentTo(self.structure_node)
            collar.setPos(cx, cy, 0.125)

    def _build_customer_lounge(self) -> None:
        """Constructs VIP customer lounge with designer modern sofas and showroom video screen."""
        lounge_root = self.furniture_node.attachNewNode("customer_lounge")

        # Positioned at right area: X = 20.0, Y = 14.0
        # 1. Large L-shaped modern minimalist sofa
        sofa_mat = Material("sofa_mat")
        sofa_mat.setDiffuse(Vec4(0.22, 0.24, 0.26, 1.0))
        sofa_mat.setRoughness(0.7)

        # Sofa base section 1 (parallel to X)
        s1 = self._create_box("sofa_section_1", dx=4.0, dy=1.2, dz=0.45, color=Vec4(0.22, 0.24, 0.26, 1.0))
        s1.reparentTo(lounge_root)
        s1.setPos(20.0, 14.0, 0.225)
        s1.setMaterial(sofa_mat)

        # Sofa backrest 1
        b1 = self._create_box("sofa_back_1", dx=4.0, dy=0.35, dz=0.45, color=Vec4(0.22, 0.24, 0.26, 1.0))
        b1.reparentTo(lounge_root)
        b1.setPos(20.0, 14.42, 0.65)
        b1.setMaterial(sofa_mat)

        # Sofa section 2 (parallel to Y)
        s2 = self._create_box("sofa_section_2", dx=1.2, dy=3.0, dz=0.45, color=Vec4(0.22, 0.24, 0.26, 1.0))
        s2.reparentTo(lounge_root)
        s2.setPos(22.6, 12.0, 0.225)
        s2.setMaterial(sofa_mat)

        # 2. Modern Marble Coffee Table
        table_top = self._create_box("coffee_table_top", dx=2.2, dy=1.2, dz=0.08, color=Vec4(0.92, 0.92, 0.95, 1.0))
        table_top.reparentTo(lounge_root)
        table_top.setPos(20.0, 12.0, 0.36)

        table_legs = self._create_box("coffee_table_legs", dx=2.0, dy=1.0, dz=0.32, color=Vec4(0.12, 0.12, 0.14, 1.0))
        table_legs.reparentTo(lounge_root)
        table_legs.setPos(20.0, 12.0, 0.16)

        # 3. Lounge Wall Promo Display Screen (X = 27.85, Y = 14.0, Z = 2.4)
        screen = self._create_quad(
            Point3(27.85, 11.0, 3.4),
            Point3(27.85, 17.0, 3.4),
            Point3(27.85, 17.0, 1.6),
            Point3(27.85, 11.0, 1.6),
            Vec3(-1, 0, 0),
            Vec4(0.05, 0.08, 0.15, 1.0),
            name="lounge_promo_screen",
        )
        screen.reparentTo(lounge_root)
        screen.setLightOff()

        # Feature architectural pillar signage: "Performance / Luxury / Innovation / Sustainability"
        brand_sign = self._create_quad(
            Point3(27.85, 18.0, 3.2),
            Point3(27.85, 20.5, 3.2),
            Point3(27.85, 20.5, 1.8),
            Point3(27.85, 18.0, 1.8),
            Vec3(-1, 0, 0),
            Vec4(0.15, 0.17, 0.20, 1.0),
            name="brand_pillars_sign",
        )
        brand_sign.reparentTo(lounge_root)

    def _build_planters_and_plants(self) -> None:
        """Constructs indoor ornamental trees and minimalist geometric planters."""
        planter_positions = [
            (-18.0, 14.0), (-18.0, -12.0),
            (4.0, 18.0),   (-4.0, 18.0),
            (14.0, 18.0),  (24.0, 6.0),
            (-26.0, 18.0), (-26.0, -18.0),
        ]

        planter_mat = Material("planter_mat")
        planter_mat.setDiffuse(Vec4(0.18, 0.19, 0.21, 1.0))
        planter_mat.setRoughness(0.5)

        foliage_mat = Material("foliage_mat")
        foliage_mat.setDiffuse(Vec4(0.12, 0.45, 0.18, 1.0))

        for i, (px, py) in enumerate(planter_positions):
            p_group = self.props_node.attachNewNode(f"planter_{i}")
            p_group.setPos(px, py, 0.0)

            # Minimalist cube planter box (0.9m x 0.9m x 0.65m)
            box = self._create_box(f"planter_box_{i}", dx=0.9, dy=0.9, dz=0.65, color=Vec4(0.18, 0.19, 0.21, 1.0))
            box.reparentTo(p_group)
            box.setPos(0, 0, 0.325)
            box.setMaterial(planter_mat)

            # Dark soil
            soil = self._create_quad(
                Point3(-0.4, -0.4, 0.64), Point3(0.4, -0.4, 0.64),
                Point3(0.4, 0.4, 0.64), Point3(-0.4, 0.4, 0.64),
                Vec3(0, 0, 1), Vec4(0.1, 0.08, 0.06, 1.0),
                name=f"soil_{i}",
            )
            soil.reparentTo(p_group)

            # Tree trunk
            trunk = self._create_box(f"trunk_{i}", dx=0.12, dy=0.12, dz=1.4, color=Vec4(0.35, 0.25, 0.18, 1.0))
            trunk.reparentTo(p_group)
            trunk.setPos(0, 0, 1.3)

            # Stylized geometric lush foliage spheres
            for oz, sc in [(1.8, 0.9), (2.3, 0.7), (2.7, 0.5)]:
                bush = self._create_box(f"bush_{i}_{oz}", dx=sc, dy=sc, dz=sc * 0.8, color=Vec4(0.14, 0.48, 0.20, 1.0))
                bush.reparentTo(p_group)
                bush.setPos(0, 0, oz)
                bush.setMaterial(foliage_mat)

    def _build_spec_kiosks(self) -> None:
        """Constructs interactive angled informational spec stands beside each vehicle platform."""
        # Kiosk positions: placed at the front edge of each platform
        kiosk_configs = [
            (0.0, -4.2, 0.0, "Centerpiece Spec Stand"),
            (12.0, 6.2, 0.0, "Hypercar Spec Stand"),
            (-12.0, 4.2, 0.0, "Supercar Spec Stand"),
            (14.0, -7.8, 0.0, "SUV Spec Stand"),
            (20.0, 0.5, 0.0, "GT Spec Stand"),
            (-14.0, -7.8, 0.0, "EV Spec Stand"),
        ]

        stand_mat = Material("kiosk_mat")
        stand_mat.setDiffuse(Vec4(0.12, 0.13, 0.15, 1.0))
        stand_mat.setMetallic(0.7)

        for i, (kx, ky, kz, kname) in enumerate(kiosk_configs):
            k_node = self.kiosks_node.attachNewNode(f"kiosk_{i}")
            k_node.setPos(kx, ky, kz)

            # Weighted base plate
            base = self._create_box(f"kiosk_base_{i}", dx=0.6, dy=0.5, dz=0.06, color=Vec4(0.12, 0.13, 0.15, 1.0))
            base.reparentTo(k_node)
            base.setPos(0, 0, 0.03)

            # Upright angled vertical stanchion
            pole = self._create_box(f"kiosk_pole_{i}", dx=0.10, dy=0.10, dz=0.9, color=Vec4(0.2, 0.22, 0.25, 1.0))
            pole.reparentTo(k_node)
            pole.setPos(0, 0, 0.5)

            # Angled display tablet panel (35-degree tilt)
            tablet = self._create_box(f"kiosk_screen_{i}", dx=0.65, dy=0.45, dz=0.04, color=Vec4(0.08, 0.10, 0.14, 1.0))
            tablet.reparentTo(k_node)
            tablet.setPos(0, 0, 0.98)
            tablet.setP(-35.0)

            # Glowing tablet screen face
            screen = self._create_quad(
                Point3(-0.29, -0.19, 0.025), Point3(0.29, -0.19, 0.025),
                Point3(0.29, 0.19, 0.025), Point3(-0.29, 0.19, 0.025),
                Vec3(0, 0, 1), Vec4(0.15, 0.25, 0.40, 1.0),
                name=f"screen_face_{i}",
            )
            screen.reparentTo(tablet)
            screen.setLightOff()

            # Glowing blue interactive indicator ring on floor in front of kiosk
            ring = self._create_interactive_floor_ring(f"ring_{i}", radius=0.8)
            ring.reparentTo(k_node)
            ring.setPos(0, -0.6, 0.01)

    def _create_interactive_floor_ring(self, name: str, radius: float = 0.8, segments: int = 24) -> NodePath:
        """Creates a subtle pulsating interaction ring on the floor."""
        node = NodePath(name)
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData(f"{name}_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)

        c_ring = Vec4(0.2, 0.7, 1.0, 0.8)
        r_inner = radius - 0.06
        r_outer = radius

        angles = [i * 2.0 * math.pi / segments for i in range(segments + 1)]
        for i in range(segments):
            a1, a2 = angles[i], angles[i + 1]
            p1 = Point3(math.cos(a1) * r_inner, math.sin(a1) * r_inner, 0)
            p2 = Point3(math.cos(a2) * r_inner, math.sin(a2) * r_inner, 0)
            p3 = Point3(math.cos(a2) * r_outer, math.sin(a2) * r_outer, 0)
            p4 = Point3(math.cos(a1) * r_outer, math.sin(a1) * r_outer, 0)

            idx = vertex.getWriteRow()
            for p in (p1, p2, p3, p4):
                vertex.addData3(p); normal.addData3(0, 0, 1); color.addData4(c_ring)
            tris.addVertices(idx, idx + 1, idx + 2)
            tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode(f"{name}_geom")
        gnode.addGeom(geom)
        np = node.attachNewNode(gnode)
        np.setLightOff()
        np.setTransparency(TransparencyAttrib.M_alpha)
        return node

    def _setup_lighting(self) -> None:
        """Sets up high-end architectural showroom illumination."""
        # 1. Warm indirect ambient light
        alight = AmbientLight("ambient_light")
        alight.setColor(Vec4(0.42, 0.44, 0.48, 1.0))
        alnp = self.lighting_node.attachNewNode(alight)
        self.render.setLight(alnp)

        # 2. Cool directional daylight entering through the panoramic glass facade
        dlight = DirectionalLight("daylight")
        dlight.setColor(Vec4(0.85, 0.88, 0.95, 1.0))
        dlnp = self.lighting_node.attachNewNode(dlight)
        # Coming from top-left through the panoramic window (X < 0)
        dlnp.setHpr(-65, -35, 0)
        self.render.setLight(dlnp)

        # 3. Soft warm fill light from showroom interior
        fill_light = DirectionalLight("interior_fill")
        fill_light.setColor(Vec4(0.45, 0.40, 0.35, 1.0))
        fill_np = self.lighting_node.attachNewNode(fill_light)
        fill_np.setHpr(115, -20, 0)
        self.render.setLight(fill_np)

        # 4. Spotlights focused downward on each platform
        spot_targets = [
            (0.0, 0.0, "spot_center"),
            (12.0, 10.0, "spot_hypercar"),
            (-12.0, 8.0, "spot_supercar"),
            (14.0, -4.0, "spot_suv"),
            (20.0, 4.0, "spot_gt"),
            (-14.0, -4.0, "spot_ev"),
        ]

        for sx, sy, sname in spot_targets:
            slight = Spotlight(sname)
            slight.setColor(Vec4(1.0, 0.98, 0.95, 1.0))
            lens = PerspectiveLens()
            lens.setFov(45.0)
            slight.setLens(lens)
            slnp = self.lighting_node.attachNewNode(slight)
            slnp.setPos(sx, sy, 8.5)
            slnp.lookAt(Point3(sx, sy, 0.2))
            self.render.setLight(slnp)

    # ---------------- Geometry Utility Helpers ----------------

    def _create_quad(
        self,
        p1: Point3,
        p2: Point3,
        p3: Point3,
        p4: Point3,
        norm: Vec3,
        col: Vec4,
        name: str = "quad",
    ) -> NodePath:
        """Creates a single textured quad polygon."""
        vformat = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData(f"{name}_data", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        tris = GeomTriangles(Geom.UHStatic)

        idx = vertex.getWriteRow()
        vertex.addData3(p1); normal.addData3(norm); color.addData4(col); texcoord.addData2(0, 1)
        vertex.addData3(p2); normal.addData3(norm); color.addData4(col); texcoord.addData2(1, 1)
        vertex.addData3(p3); normal.addData3(norm); color.addData4(col); texcoord.addData2(1, 0)
        vertex.addData3(p4); normal.addData3(norm); color.addData4(col); texcoord.addData2(0, 0)

        tris.addVertices(idx, idx + 1, idx + 2)
        tris.addVertices(idx, idx + 2, idx + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        gnode = GeomNode(f"{name}_geom")
        gnode.addGeom(geom)
        return NodePath(gnode)

    def _create_box(
        self,
        name: str,
        dx: float,
        dy: float,
        dz: float,
        color: Vec4,
    ) -> NodePath:
        """Constructs an axis-aligned 3D box centered at origin."""
        root = NodePath(name)
        hx, hy, hz = dx * 0.5, dy * 0.5, dz * 0.5

        # 6 Faces
        faces = [
            (Point3(-hx, -hy, hz), Point3(hx, -hy, hz), Point3(hx, hy, hz), Point3(-hx, hy, hz), Vec3(0, 0, 1)),     # Top
            (Point3(-hx, hy, -hz), Point3(hx, hy, -hz), Point3(hx, -hy, -hz), Point3(-hx, -hy, -hz), Vec3(0, 0, -1)),  # Bottom
            (Point3(-hx, -hy, -hz), Point3(hx, -hy, -hz), Point3(hx, -hy, hz), Point3(-hx, -hy, hz), Vec3(0, -1, 0)),  # Front
            (Point3(hx, hy, -hz), Point3(-hx, hy, -hz), Point3(-hx, hy, hz), Point3(hx, hy, hz), Vec3(0, 1, 0)),      # Back
            (Point3(-hx, hy, -hz), Point3(-hx, -hy, -hz), Point3(-hx, -hy, hz), Point3(-hx, hy, hz), Vec3(-1, 0, 0)),  # Left
            (Point3(hx, -hy, -hz), Point3(hx, hy, -hz), Point3(hx, hy, hz), Point3(hx, -hy, hz), Vec3(1, 0, 0)),      # Right
        ]

        for i, (p1, p2, p3, p4, norm) in enumerate(faces):
            q = self._create_quad(p1, p2, p3, p4, norm, color, name=f"{name}_f{i}")
            q.reparentTo(root)

        return root
