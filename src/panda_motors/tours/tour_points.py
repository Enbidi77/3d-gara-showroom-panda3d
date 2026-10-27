"""Waypoints and narrative captions for the showroom guided tour."""

from dataclasses import dataclass


@dataclass
class TourWaypoint:
    title: str
    caption: str
    camera_pos: tuple[float, float, float]
    look_target: tuple[float, float, float]
    duration_seconds: float = 6.0
    transition_seconds: float = 2.2
    featured_vehicle_id: str = ""


TOUR_WAYPOINTS: list[TourWaypoint] = [
    TourWaypoint(
        title="Grand Entrance — Panoramic Lake View",
        caption="Welcome to Panda Motors Flagship Showroom. Floor-to-ceiling panoramic glass windows reveal stunning mountain vistas and modern skyline reflections across the bay.",
        camera_pos=(0.0, -22.0, 5.0),
        look_target=(0.0, 6.0, 1.2),
        duration_seconds=6.5,
        transition_seconds=2.5,
    ),
    TourWaypoint(
        title="Centerpiece Rotunda — Panda Corsa 750 GT",
        caption="Our flagship track-bred Italian supercar features an ultra-light carbon monocoque, twin-turbo V8 producing 740 hp, and 0-100 km/h in 2.8 seconds.",
        camera_pos=(3.5, -4.5, 2.2),
        look_target=(0.0, 0.0, 0.8),
        duration_seconds=7.0,
        transition_seconds=2.0,
        featured_vehicle_id="panda_corsa_gt",
    ),
    TourWaypoint(
        title="Supercar Gallery — Carrera 4S Performance",
        caption="Positioned along the waterfront gallery, the Carrera 4S embodies pure precision with its twin-turbo flat-six and active torque vectoring.",
        camera_pos=(-9.0, 4.0, 2.4),
        look_target=(-12.0, 8.0, 0.9),
        duration_seconds=6.5,
        transition_seconds=2.2,
        featured_vehicle_id="porsche_911_gt3",
    ),
    TourWaypoint(
        title="Hypercar Exhibition — Apex SVJ",
        caption="Extreme aerodynamic efficiency and naturally aspirated V12 fury. The SVJ Apex features active ALA 2.0 aero vectoring and forged composite wings.",
        camera_pos=(8.5, 7.0, 2.2),
        look_target=(12.0, 10.0, 0.9),
        duration_seconds=7.0,
        transition_seconds=2.2,
        featured_vehicle_id="aventador_svj",
    ),
    TourWaypoint(
        title="Luxury Collection — Titan SRT & Empress RT",
        caption="Executive presence meets ferocious capability. Sumptuous Laguna leather, acoustic glazing, and powerful V8 authority.",
        camera_pos=(12.0, -9.0, 2.5),
        look_target=(14.0, -4.0, 1.1),
        duration_seconds=6.5,
        transition_seconds=2.0,
        featured_vehicle_id="jeep_cherokee_srt",
    ),
    TourWaypoint(
        title="Electric Mobility Zone — Vision Quantum Concept",
        caption="Pioneering the next era of high performance: quad solid-state electric motors producing 1,150 hp, intelligent digital aero, and zero emissions.",
        camera_pos=(-10.5, -8.0, 2.2),
        look_target=(-14.0, -4.0, 0.9),
        duration_seconds=7.0,
        transition_seconds=2.2,
        featured_vehicle_id="cyber_vision_concept",
    ),
    TourWaypoint(
        title="VIP Customer Lounge & Mezzanine",
        caption="Unwind in the designer hospitality lounge featuring Italian designer seating, brand film screening, and private consultation studios.",
        camera_pos=(16.0, 8.0, 3.5),
        look_target=(21.0, 14.0, 1.2),
        duration_seconds=6.0,
        transition_seconds=2.2,
    ),
]
