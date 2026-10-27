"""Visual showcase capture script to verify showroom rendering and UI."""

import os

from panda3d.core import Point3

from panda_motors.app.application import PandaMotorsApp


def main():
    os.makedirs("showcase", exist_ok=True)
    print("Initializing application in headless mode...")
    app = PandaMotorsApp(headless=True)

    # 1. Capture Main Showroom Exploration View
    app.enter_showroom()
    app.cam.setPos(0, -14, 2.5)
    app.cam.lookAt(Point3(0, 0, 1.0))
    for _ in range(5):
        app.taskMgr.step()
    app.screenshot("showcase/01_showroom_exploration.png", defaultFilename=False)
    print("Saved showcase/01_showroom_exploration.png")

    # 2. Capture Vehicle Inspection Mode on Centerpiece Ferrari
    app.inspect_vehicle_by_id("panda_corsa_gt")
    for _ in range(5):
        app.taskMgr.step()
    app.screenshot("showcase/02_vehicle_inspection.png", defaultFilename=False)
    print("Saved showcase/02_vehicle_inspection.png")

    # 3. Capture Vehicle Catalog Browser
    app.open_catalog()
    for _ in range(5):
        app.taskMgr.step()
    app.screenshot("showcase/03_vehicle_catalog.png", defaultFilename=False)
    print("Saved showcase/03_vehicle_catalog.png")

    # 4. Capture Panoramic Window Facade & Supercar Gallery
    app.enter_showroom()
    app.nav_service.travel_to_zone("supercar_gallery", smooth=False)
    for _ in range(5):
        app.taskMgr.step()
    app.screenshot("showcase/04_supercar_gallery.png", defaultFilename=False)
    print("Saved showcase/04_supercar_gallery.png")

    app.destroy()
    print("All showcase captures completed successfully!")

if __name__ == "__main__":
    main()
