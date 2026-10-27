"""Main application orchestrator coordinating engine, world, vehicles, UI, and navigation."""

import logging
import math
import sys

import simplepbr
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AntialiasAttrib,
    ClockObject,
    Point3,
    WindowProperties,
    loadPrcFileData,
)

from panda_motors.app.config_manager import ConfigManager
from panda_motors.app.state_manager import AppState, StateManager
from panda_motors.audio.audio_manager import AudioManager
from panda_motors.core.asset_manager import AssetManager
from panda_motors.core.events import EventBus
from panda_motors.core.performance import PerformanceMonitor
from panda_motors.navigation.camera_controller import CameraController
from panda_motors.navigation.minimap import MinimapHUD
from panda_motors.navigation.navigation_service import NavigationService
from panda_motors.navigation.player_controller import PlayerController
from panda_motors.tours.tour_manager import TourManager
from panda_motors.ui.hud import HUD
from panda_motors.ui.main_menu import MainMenuScreen
from panda_motors.ui.navigation_menu import NavigationMenuModal
from panda_motors.ui.settings_panel import SettingsPanel
from panda_motors.ui.theme_manager import ThemeManager
from panda_motors.ui.vehicle_browser import VehicleBrowserScreen
from panda_motors.ui.vehicle_details import VehicleDetailsPanel
from panda_motors.vehicles.configurator import VehicleConfigurator
from panda_motors.vehicles.vehicle_catalog import VehicleCatalog
from panda_motors.vehicles.vehicle_inspector import VehicleInspector
from panda_motors.vehicles.vehicle_loader import VehicleLoader
from panda_motors.world.collision_world import CollisionWorld
from panda_motors.world.showroom_builder import ShowroomBuilder
from panda_motors.world.showroom_zones import ShowroomZoneRegistry

logger = logging.getLogger(__name__)


class PandaMotorsApp(ShowBase):
    """Flagship Panda Motors 3D Showroom Application."""

    def __init__(self, headless: bool = False) -> None:
        self.config_manager = ConfigManager()

        if headless:
            loadPrcFileData("", "window-type offscreen")
        else:
            w = self.config_manager.get_app("graphics.active.resolution_x", 1280)
            h = self.config_manager.get_app("graphics.active.resolution_y", 720)
            loadPrcFileData("", f"win-size {w} {h}")
            loadPrcFileData("", "sync-video true")
            loadPrcFileData("", "textures-power-2 none")

        ShowBase.__init__(self)

        # Set window title if real window exists
        wp = WindowProperties()
        wp.setTitle("Panda Motors — Interactive 3D Luxury Car Showroom")
        if hasattr(self.win, "requestProperties"):
            self.win.requestProperties(wp)

        # Initialize simplepbr PBR rendering pipeline
        self.pbr_pipeline = simplepbr.init(enable_shadows=False, msaa_samples=4)
        self.render.setAntialias(AntialiasAttrib.MAuto)

        # Core Services
        self.event_bus = EventBus.get_instance()
        self.state_manager = StateManager(AppState.MAIN_MENU)
        self.perf_monitor = PerformanceMonitor()
        self.asset_manager = AssetManager(self.loader)
        self.audio_manager = AudioManager(self, self.asset_manager)
        self.theme_manager = ThemeManager(self.config_manager.get_app("ui.theme", "dark"))

        # World, Zones & Collision
        self.zone_registry = ShowroomZoneRegistry()
        self.collision_world = CollisionWorld(self.render)
        self.collision_world.setup_environment_collisions()

        # Build 3D Showroom Architecture
        self.builder = ShowroomBuilder(self.render, self.asset_manager)
        self.showroom_root = self.builder.build_all()

        # Load Vehicles Catalog & Spawn on Platforms
        self.catalog = VehicleCatalog()
        self.vehicle_loader = VehicleLoader(
            self.render, self.asset_manager, self.catalog, self.collision_world
        )
        self.live_vehicles = self.vehicle_loader.spawn_all_vehicles(self.builder.platform_transforms)

        # Camera & Navigation Controllers
        self.camera_controller = CameraController(self.cam)
        self.player_controller = PlayerController(self, self.collision_world, self.asset_manager)
        self.nav_service = NavigationService(self.zone_registry, self.player_controller, self.camera_controller)
        self.minimap = MinimapHUD(self.aspect2d, self.player_controller)

        # Vehicle Inspector & Configurator
        self.inspector = VehicleInspector(self.cam)
        self.configurator = VehicleConfigurator()

        # Guided Tour
        self.tour_manager = TourManager(self.camera_controller)

        # User Interface Layers
        self._init_ui()

        # Input & Keybindings
        self._setup_keybindings()

        # Subscribe to internal events
        self._subscribe_events()

        # Main frame update loop task
        self.taskMgr.add(self.update_loop, "update_loop")

        # Set initial state
        if not headless:
            self._set_cinematic_menu_camera()
            self.main_menu.show()
            self.hud.root.hide()
            self.minimap.hide()

    def _init_ui(self) -> None:
        """Initializes all 2D UI panels and screens."""
        self.hud = HUD(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            perf_monitor=self.perf_monitor,
            on_nav_tab_click=self._handle_nav_tab_click,
            on_category_click=self._handle_category_filter,
            on_view_preset_click=self._handle_view_preset,
            on_settings_click=self._open_settings,
        )

        self.main_menu = MainMenuScreen(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            on_enter_showroom=self.enter_showroom,
            on_open_catalog=self.open_catalog,
            on_open_configurator=self.open_configurator_studio,
            on_start_tour=self.start_guided_tour,
            on_open_settings=self._open_settings,
            on_exit_app=self.exit_application,
        )

        self.nav_modal = NavigationMenuModal(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            zone_registry=self.zone_registry,
            on_select_zone=self._teleport_to_zone,
            on_start_tour=self.start_guided_tour,
            on_close=self.close_modals,
        )

        self.browser_screen = VehicleBrowserScreen(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            catalog=self.catalog,
            on_select_vehicle=self.inspect_vehicle_by_id,
            on_close=self.close_modals,
        )

        self.vehicle_details = VehicleDetailsPanel(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            inspector=self.inspector,
            configurator=self.configurator,
            on_exit=self.exit_inspection,
        )

        self.settings_panel = SettingsPanel(
            parent_2d=self.aspect2d,
            theme_manager=self.theme_manager,
            audio_manager=self.audio_manager,
            on_preset_change=self.apply_graphics_preset,
            on_toggle_theme=self.toggle_theme,
            on_close=self.close_modals,
        )

    def _setup_keybindings(self) -> None:
        """Binds keyboard inputs and mouse events."""
        # Movement WASD
        self.accept("w", self.player_controller.set_key_state, ["forward", True])
        self.accept("w-up", self.player_controller.set_key_state, ["forward", False])
        self.accept("s", self.player_controller.set_key_state, ["backward", True])
        self.accept("s-up", self.player_controller.set_key_state, ["backward", False])
        self.accept("a", self.player_controller.set_key_state, ["left", True])
        self.accept("a-up", self.player_controller.set_key_state, ["left", False])
        self.accept("d", self.player_controller.set_key_state, ["right", True])
        self.accept("d-up", self.player_controller.set_key_state, ["right", False])
        self.accept("shift", self.player_controller.set_key_state, ["sprint", True])
        self.accept("shift-up", self.player_controller.set_key_state, ["sprint", False])

        # Actions
        self.accept("e", self._handle_interact_action)
        self.accept("f", self.player_controller.toggle_perspective)
        self.accept("tab", self._toggle_nav_modal)
        self.accept("escape", self._handle_escape_action)
        self.accept("h", self.hud.toggle_visibility)
        self.accept("f11", self._toggle_fullscreen)

        # Mouse clicks & mouse look
        self.accept("mouse1", self._on_mouse_down)
        self.accept("mouse1-up", self._on_mouse_up)
        self.accept("wheel_up", self._on_wheel_up)
        self.accept("wheel_down", self._on_wheel_down)

        self._mouse_down: bool = False
        self._last_mouse_x: float = 0.0
        self._last_mouse_y: float = 0.0

    def _on_mouse_down(self) -> None:
        self._mouse_down = True
        if self.mouseWatcherNode.hasMouse():
            self._last_mouse_x = self.mouseWatcherNode.getMouseX()
            self._last_mouse_y = self.mouseWatcherNode.getMouseY()
            if self.state_manager.current_state == AppState.EXPLORATION:
                self.player_controller.mouse_look_enabled = True

    def _on_mouse_up(self) -> None:
        self._mouse_down = False
        if self.state_manager.current_state == AppState.EXPLORATION:
            self.player_controller.mouse_look_enabled = False

    def _on_wheel_up(self) -> None:
        if self.state_manager.current_state in (AppState.INSPECTION, AppState.CONFIGURATOR):
            self.inspector.zoom_orbit(0.5)

    def _on_wheel_down(self) -> None:
        if self.state_manager.current_state in (AppState.INSPECTION, AppState.CONFIGURATOR):
            self.inspector.zoom_orbit(-0.5)

    def _subscribe_events(self) -> None:
        """Hooks into global event bus."""
        self.event_bus.subscribe("on_zone_changed", self._on_zone_changed)
        self.event_bus.subscribe("on_tour_stopped", self._on_tour_stopped)

    def _on_zone_changed(self, old_zone, new_zone) -> None:
        if new_zone:
            self.hud.set_zone_info(new_zone.name, new_zone.description[:35] + "...")

    def _on_tour_stopped(self) -> None:
        self.enter_showroom()

    # ---------------- State Transitions & Actions ----------------

    def enter_showroom(self) -> None:
        """Transitions into live 3D exploration mode."""
        self.main_menu.hide()
        self.browser_screen.hide()
        self.vehicle_details.hide()
        self.nav_modal.hide()
        self.settings_panel.hide()

        self.state_manager.change_state(AppState.EXPLORATION)
        self.hud.root.show()
        self.minimap.show()
        self.audio_manager.play_ui_click()

    def open_catalog(self) -> None:
        """Opens full-screen vehicle catalog browser."""
        self.state_manager.change_state(AppState.CATALOG_BROWSER)
        self.browser_screen.show()
        self.audio_manager.play_ui_click()

    def open_configurator_studio(self) -> None:
        """Navigates directly to the center flagship car in inspection/configurator mode."""
        self.enter_showroom()
        self.inspect_vehicle_by_id("panda_corsa_gt")

    def start_guided_tour(self) -> None:
        """Launches the cinematic guided tour."""
        self.close_modals()
        self.main_menu.hide()
        self.hud.root.show()
        self.minimap.show()

        self.state_manager.change_state(AppState.GUIDED_TOUR)
        self.tour_manager.start_tour()
        self.audio_manager.play_ui_click()

    def inspect_vehicle_by_id(self, vehicle_id: str) -> None:
        """Transitions into focused vehicle inspection mode."""
        veh = self.vehicle_loader.get_live_vehicle(vehicle_id)
        if not veh:
            return

        self.close_modals()
        self.main_menu.hide()
        self.state_manager.change_state(AppState.INSPECTION)

        self.inspector.enter_inspection(veh)
        self.vehicle_details.show_vehicle(veh)
        self.hud.root.hide()
        self.minimap.hide()

        self.audio_manager.play_ui_click()
        self.audio_manager.play_engine_rev()

    def exit_inspection(self) -> None:
        """Restores exploration state from vehicle inspection."""
        self.inspector.exit_inspection()
        self.vehicle_details.hide()
        self.enter_showroom()

    def _teleport_to_zone(self, zone_id: str) -> None:
        self.close_modals()
        self.nav_service.travel_to_zone(zone_id, smooth=True)
        self.audio_manager.play_ui_click()

    def _open_settings(self) -> None:
        self.settings_panel.show()
        self.audio_manager.play_ui_click()

    def close_modals(self) -> None:
        """Closes all active modal windows."""
        self.nav_modal.hide()
        self.browser_screen.hide()
        self.settings_panel.hide()

    def _handle_interact_action(self) -> None:
        """Interacts with nearest vehicle or kiosk."""
        if self.state_manager.current_state == AppState.EXPLORATION:
            probed_id = self.collision_world.get_probed_interactive_object()
            if probed_id:
                self.inspect_vehicle_by_id(probed_id)
            else:
                # If near center, inspect flagship
                pos = self.player_controller.position
                dist_center = pos.length()
                if dist_center < 7.0:
                    self.inspect_vehicle_by_id("panda_corsa_gt")

    def _handle_escape_action(self) -> None:
        """Handles Escape key contextually."""
        curr = self.state_manager.current_state
        if curr == AppState.INSPECTION:
            self.exit_inspection()
        elif curr in (AppState.CATALOG_BROWSER, AppState.SETTINGS):
            self.close_modals()
            self.enter_showroom()
        elif curr == AppState.GUIDED_TOUR:
            self.tour_manager.stop_tour()
        elif curr == AppState.EXPLORATION:
            self.settings_panel.toggle()

    def _toggle_nav_modal(self) -> None:
        if self.state_manager.current_state == AppState.EXPLORATION:
            self.nav_modal.toggle()
            self.audio_manager.play_ui_click()

    def _toggle_fullscreen(self) -> None:
        wp = WindowProperties()
        wp.setFullscreen(not self.win.getProperties().getFullscreen())
        self.win.requestProperties(wp)

    def _handle_nav_tab_click(self, tab_name: str) -> None:
        self.audio_manager.play_ui_click()
        if tab_name == "Home":
            self.state_manager.change_state(AppState.MAIN_MENU)
            self._set_cinematic_menu_camera()
            self.main_menu.show()
            self.hud.root.hide()
            self.minimap.hide()
        elif tab_name == "Showroom":
            self.enter_showroom()
        elif tab_name == "Collection":
            self.open_catalog()
        elif tab_name == "Tour":
            self.start_guided_tour()

    def _handle_category_filter(self, category: str) -> None:
        self.audio_manager.play_ui_click()
        # Find zone corresponding to category
        zone_map = {
            "Supercars": "supercar_gallery",
            "Hypercars": "hypercar_exhibition",
            "SUVs": "luxury_collection",
            "Luxury sedans": "luxury_collection",
            "Electric": "electric_zone",
            "All Cars": "main_showroom",
        }
        target_zone = zone_map.get(category, "main_showroom")
        self._teleport_to_zone(target_zone)

    def _handle_view_preset(self, zone_id: str) -> None:
        self._teleport_to_zone(zone_id)

    def _set_cinematic_menu_camera(self) -> None:
        """Sets an elevated panoramic camera angle for the main opening screen."""
        self.cam.setPos(0.0, -22.0, 5.2)
        self.cam.lookAt(Point3(0.0, 6.0, 1.2))

    def apply_graphics_preset(self, preset_name: str) -> None:
        """Applies rendering quality preset (Low, Medium, High, Ultra)."""
        logger.info(f"Applying graphics preset: {preset_name}")
        preset = self.config_manager.get_graphics_preset(preset_name)
        msaa = preset.get("msaa_samples", 4)
        if self.pbr_pipeline:
            self.pbr_pipeline.msaa_samples = msaa

    def toggle_theme(self) -> None:
        new_theme = self.theme_manager.toggle_theme()
        logger.info(f"Switched UI theme to: {new_theme}")

    def exit_application(self) -> None:
        sys.exit(0)

    # ---------------- Frame Loop Update ----------------

    def update_loop(self, task) -> int:
        clock = ClockObject.getGlobalClock()
        dt = clock.getDt()
        self.perf_monitor.update()
        self.hud.update()

        # Handle mouse drag in inspection mode or exploration
        if self._mouse_down and self.mouseWatcherNode.hasMouse():
            mx = self.mouseWatcherNode.getMouseX()
            my = self.mouseWatcherNode.getMouseY()
            dx = (mx - self._last_mouse_x) * 100.0
            dy = (my - self._last_mouse_y) * 100.0
            self._last_mouse_x = mx
            self._last_mouse_y = my

            if self.state_manager.current_state in (AppState.INSPECTION, AppState.CONFIGURATOR):
                self.inspector.rotate_orbit(dx * 0.4, dy * 0.4)
            elif self.state_manager.current_state == AppState.EXPLORATION:
                self.player_controller.handle_mouse_move(dx * 0.25, dy * 0.25)

        curr_state = self.state_manager.current_state

        if curr_state == AppState.EXPLORATION:
            self.player_controller.update(dt)
            self.nav_service.update()
            self.minimap.update()

            # Check for nearby interactive vehicle
            probed_id = self.collision_world.get_probed_interactive_object()
            if probed_id:
                veh = self.vehicle_loader.get_live_vehicle(probed_id)
                vname = veh.data.display_name if veh else probed_id
                self.hud.show_interaction_prompt(vname)
            else:
                self.hud.hide_interaction_prompt()

        elif curr_state == AppState.GUIDED_TOUR:
            self.camera_controller.update(dt)
            self.tour_manager.update(dt)
            self.minimap.update()

        elif curr_state == AppState.MAIN_MENU:
            # Subtle gentle camera pan for opening screen
            t = clock.getFrameTime() * 0.15
            cam_x = math.sin(t) * 1.5
            self.cam.setPos(cam_x, -22.0, 5.2)
            self.cam.lookAt(Point3(0.0, 6.0, 1.2))

        # Update all active vehicles (turntables, animations)
        self.vehicle_loader.update_all(dt)

        return task.cont
