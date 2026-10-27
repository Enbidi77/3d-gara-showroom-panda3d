# Panda Motors — Interactive 3D Luxury Car Showroom

> *"Explore. Discover. Drive."*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Panda3D](https://img.shields.io/badge/Panda3D-1.10.16-orange.svg)](https://www.panda3d.org/)
[![PBR](https://img.shields.io/badge/Rendering-SimplePBR-success.svg)](https://github.com/Moguri/panda3d-simplepbr)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://docs.pytest.org/)
[![Code Style](https://img.shields.io/badge/ruff-clean-blue.svg)](https://github.com/astral-sh/ruff)
[![Type Checked](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)

**Panda Motors** is a luxury automotive digital experience combining high-end architectural design, real-time 3D vehicle inspection, an interactive vehicle configurator, and smooth 1st/3rd-person exploration powered by **Python and Panda3D**.

---

## 1. Features Overview

### 🏛️ Architectural Luxury Showroom
- **Monumental Panoramic Glass Facade**: Floor-to-ceiling glass wall overlooking a sparkling bay, mountain peaks, and modern skyline under natural daylight.
- **Reflective Glossy Marble Floor**: High-resolution PolyHaven Carrara marble with specular reflections, normal mapping, and environmental shine.
- **Circular Raised Display Platforms**: 6 custom exhibition rotundas with chamfered rim lighting and glowing LED neon borders.
- **Suspended Overhead Ring Lights**: Dual-ring illuminated torus lighting fixtures centered over every vehicle.
- **Iconic Central Feature Wall**: Dark textured acoustic feature wall showcasing the glowing white **Panda Motors** logo emblem (*"Drive Your Dreams"*).
- **VIP Customer Lounge & Mezzanine**: Italian designer L-shaped sofas, marble coffee tables, promotional video display screens, and upper glass-balustrade mezzanine.
- **Indoor Landscaping & Kiosks**: Ornamental potted trees in minimalist planters and interactive angled digital specification stands beside each platform.

### 🏎️ Vehicle Fleet & Configurator Studio
- **Panda Corsa 750 GT** (Supercar) — 4.0L Twin-Turbo V8, 740 HP, 0-100 km/h in 2.8s.
- **Panda SV Hypercar Apex** (Hypercar) — 6.5L Naturally Aspirated V12, 770 HP, active aero ALA 2.0.
- **Panda Carrera 4S** (Sports Coupe) — 3.0L Twin-Turbo Boxer 6, 450 HP, all-wheel drive.
- **Panda Titan SRT Luxury SUV** (Performance SUV) — 6.4L HEMI V8, 475 HP, Brembo brakes.
- **Panda Empress RT Executive** (Luxury Sedan) — 5.7L V8 MDS, 370 HP, executive grand touring comfort.
- **Panda Vision E-Quantum Concept** (Electric Hyper-Coupe) — Quad solid-state motors, 1,150 HP, 0-100 in 1.95s.
- **Real-Time 3D Paint Configurator**: Dynamically alters paint hue, metallic, matte, and gloss finishes on live 3D models.
- **Vehicle Inspection Mode**: 360° mouse-drag orbit camera, preset camera viewpoints (Front, Rear, Side, Wheel close-up, Top), turntable slow rotation, and headlight emission toggles.
- **Procedural Vehicle Fallback**: Intelligent fallback system that builds streamlined sports car geometry if any external asset is missing.

### 🎮 Exploration & Navigation
- **Dual Perspectives**: Toggle seamlessly between third-person character exploration (with an animated visitor avatar) and immersive first-person camera (`F` key).
- **Collision World**: Solid collision bounds prevent walking through outer glass walls, structural columns, furniture, and vehicles.
- **Interactive Minimap Radar**: Real-time HUD radar showing showroom boundaries, platform blips, cardinal directions (N/S/E/W), and player position/heading.
- **Showroom Fast Travel**: Instant navigation modal (`Tab`) with 9 curated destinations across the showroom.
- **Cinematic Guided Tour**: Automated multi-waypoint tour with smooth camera paths and narrative architectural captions.

### 🎨 User Interface & Audio
- **Apple-Inspired Translucent Glass Aesthetic**: Dark and Light theme options with frosted panels, fine borders, and clean typography.
- **Full-Screen Vehicle Collection Browser**: Search, filter by category, sort by power/speed/price, star favorites, and compare vehicles side-by-side.
- **Dynamic Audio Design**: Atmospheric showroom ventilation hum, subtle marble footsteps, crisp glass UI clicks, and V8 engine revs with volume controls.

---

## 2. Project Architecture

```
panda-motors/
├── pyproject.toml              # Project dependencies, build system, ruff/mypy configs
├── README.md                   # Complete architectural guide and user manual
├── config/
│   ├── app.toml                # App settings, window resolution, audio, UI theme
│   ├── graphics.toml           # Quality presets (Low, Medium, High, Ultra)
│   └── controls.toml           # Keybindings, mouse sensitivity, camera heights
├── assets/
│   ├── models/
│   │   ├── showroom/           # Showroom architectural assets
│   │   ├── vehicles/           # High-quality BAM/GLB vehicle models
│   │   ├── characters/         # Character avatar models (xbot.bam)
│   │   └── props/              # Showroom furniture and accessories
│   ├── textures/
│   │   ├── marble/             # PolyHaven 1K diffuse, normal, and roughness textures
│   │   ├── env/                # 360° skyline panorama and cubemap reflections
│   │   └── ui/                 # Panda Motors logos, badges, and UI icons
│   └── audio/                  # Showroom ambience, UI clicks, footsteps, engine revs
├── data/
│   ├── vehicles.json           # Structured vehicle catalog and technical specifications
│   └── showroom_zones.json     # Showroom zones, camera angles, and platform coordinates
├── src/
│   └── panda_motors/
│       ├── __init__.py
│       ├── main.py             # CLI entry point and argument parser
│       ├── app/
│       │   ├── application.py  # Central application coordinator
│       │   ├── state_manager.py# State machine (Menu, Explore, Inspect, Tour, etc.)
│       │   └── config_manager.py # TOML configuration loader and settings cache
│       ├── core/
│       │   ├── events.py       # Decoupled publish-subscribe event bus
│       │   ├── asset_manager.py# Asset loader, model caching, and procedural fallback
│       │   └── performance.py  # FPS counter and frame latency monitor
│       ├── world/
│       │   ├── showroom_builder.py # Full 3D showroom geometry, materials, and lights
│       │   ├── showroom_zones.py   # Zone metadata and spatial queries
│       │   └── collision_world.py  # Collision masks, pushers, and interaction triggers
│       ├── navigation/
│       │   ├── player_controller.py # WASD movement, mouse look, sprint, 1st/3rd toggle
│       │   ├── camera_controller.py # Smooth cinematic camera transitions
│       │   ├── navigation_service.py # Zone teleportation and travel coordinator
│       │   └── minimap.py          # Circular radar HUD floor plan
│       ├── vehicles/
│       │   ├── vehicle.py          # Live Vehicle instance & material controller
│       │   ├── vehicle_catalog.py  # Vehicle query, search, sort, and comparison
│       │   ├── vehicle_loader.py   # Spawns vehicles on platforms
│       │   ├── vehicle_inspector.py# Orbit camera and inspection viewpoints
│       │   ├── configurator.py     # Real-time paint and finish customizer
│       │   └── procedural_car.py   # Procedural fallback vehicle generator
│       ├── ui/
│       │   ├── theme_manager.py    # Dark and light luxury glass themes
│       │   ├── hud.py              # Exploration HUD overlay
│       │   ├── main_menu.py        # Opening title screen
│       │   ├── navigation_menu.py  # Fast-travel destination modal
│       │   ├── vehicle_browser.py  # Full-screen catalog & side-by-side comparison
│       │   ├── vehicle_details.py  # Vehicle specs, swatches, and inspection controls
│       │   └── settings_panel.py   # Graphics presets, audio, and theme preferences
│       ├── tours/
│       │   ├── tour_points.py      # Guided tour waypoints and captions
│       │   └── tour_manager.py     # Automated tour progression
│       └── audio/
│           └── audio_manager.py    # Showroom audio and sound effects
├── tests/
│   ├── test_vehicle_catalog.py # Catalog, search, sort, and favorites tests
│   ├── test_config.py          # Configuration loading and presets tests
│   ├── test_navigation_data.py # Showroom zones and spatial registry tests
│   └── test_state_and_services.py # State machine, event bus, and procedural car tests
└── tools/
    ├── validate_assets.py      # Asset integrity and metadata validator
    ├── convert_models.py       # GLB to BAM batch converter utility
    └── capture_showcase.py     # Automated offscreen screenshot verification
```

---

## 3. Installation

Ensure you have **Python 3.11+** installed.

Clone or navigate to the repository directory:

```bash
cd panda-motors
```

Install the package in editable mode with development dependencies:

```bash
pip install -e .
pip install pytest ruff mypy
```

Validate that all models, textures, configurations, and sounds are verified:

```bash
python tools/validate_assets.py
```

---

## 4. Launching the Application

### 🚗 Interactive 3D Showroom (Standard Windowed Mode)
```bash
python -m panda_motors.main
```
Or if installed as a console script:
```bash
panda-motors
```

### ⚡ Start Directly in a Specific Exhibition Zone
```bash
python -m panda_motors.main --zone hypercar_exhibition
python -m panda_motors.main --zone supercar_gallery
python -m panda_motors.main --zone luxury_collection
python -m panda_motors.main --zone electric_zone
```

### 🖥️ Headless Mode & Automated Verification
Run offscreen automated testing (renders frames, exercises physics, and exits):
```bash
python -m panda_motors.main --headless --test-frames 60
```

Capture showcase screenshots to the `showcase/` directory:
```bash
python tools/capture_showcase.py
```

---

## 5. Controls & Keybindings

| Input | Action |
| :--- | :--- |
| **W / A / S / D** | Walk forward, left, backward, right |
| **Shift** | Sprint (faster movement speed) |
| **Mouse Drag** | Look around in exploration mode / Orbit camera in inspection mode |
| **Mouse Wheel** | Zoom in / out during vehicle inspection |
| **E** | Interact with nearby vehicle or information kiosk |
| **F** | Toggle between First-Person and Third-Person camera view |
| **Tab** | Open Showroom Fast-Travel & Destinations menu |
| **Esc** | Pause / Settings menu (or return from inspection/catalog) |
| **H** | Toggle HUD visibility on / off |
| **F11** | Toggle Fullscreen window mode |

---

## 6. Showroom Destinations

1. **Main Showroom**: Grand central rotunda with the flagship Panda Corsa 750 GT supercar.
2. **Supercar Gallery**: Track-focused dynamics and the Porsche Carrera 4S beside the panoramic window.
3. **Hypercar Exhibition**: Naturally aspirated V12 performance featuring the SVJ Apex platform.
4. **Luxury Collection**: Sumptuous executive comfort with the Titan SRT SUV and Empress RT Sedan.
5. **Electric Mobility Zone**: Vision Quantum Concept hyper-coupe with quad solid-state motors.
6. **Vehicle Configuration Studio**: Studio lighting environment tailored for custom paint and finish tailoring.
7. **Customer Lounge**: VIP hospitality area with Italian designer sofas and brand promotional displays.
8. **Reception & Information Center**: Welcome foyer with interactive brochures and concierge kiosks.
9. **Outdoor Display Area**: Lakeside terrace overlooking the mountain bay.

---

## 7. Graphics Presets & Performance

Configurable in `config/graphics.toml` and via the in-game Settings panel:

- **Low**: Shadows disabled, MSAA 0x, minimal post-processing (high frame rates on integrated GPUs).
- **Medium**: Soft lighting, MSAA 2x, floor reflections enabled.
- **High** (Default): SimplePBR shaders, MSAA 4x, full environment reflections, anisotropic filtering 8x.
- **Ultra**: MSAA 8x, high-res textures, anisotropic filtering 16x, maximum draw distance.

---

## 8. Quality Assurance & Testing

Run all unit tests:
```bash
pytest
```

Run static type checking:
```bash
mypy src tests tools
```

Run code formatting and style validation:
```bash
ruff check .
```

---

## 9. Asset Attribution & Licenses

- **3D Vehicle Assets**: Sourced under open developer licenses (Three.js examples, Downtown-Driving-3D, public repositories) and converted to optimized Panda3D BAM binaries.
- **Marble Floor Texture**: PolyHaven CC0 Public Domain (`marble_01_diff_1k`, `marble_01_nor_gl_1k`, `marble_01_rough_1k`).
- **Panorama Backdrop**: PolyHaven CC0 Public Domain (`shanghai_bund` tonemapped high-resolution environment panorama).
- **Audio Effects**: Procedurally synthesized high-fidelity PCM audio buffers (ambient drone, glass UI feedback, footstep acoustics, and V8 engine revs).
- **Fallback Models**: Built-in parametric procedural sports car generator with multi-element aerodynamics, wheels, and glass canopy.

---

## 10. License

Released under the MIT License. Copyright © 2026 Panda Motors Team.

