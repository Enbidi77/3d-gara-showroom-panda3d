"""Main entry point for Panda Motors application."""

import argparse
import logging
import sys

from panda_motors.app.application import PandaMotorsApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("panda_motors")


def parse_args():
    parser = argparse.ArgumentParser(description="Panda Motors — Interactive 3D Luxury Car Showroom")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without opening an OS display window (useful for CI and testing)",
    )
    parser.add_argument(
        "--test-frames",
        type=int,
        default=0,
        help="Run for N frames and exit (for automated verification)",
    )
    parser.add_argument(
        "--zone",
        type=str,
        default="",
        help="Start immediately in a specified zone",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("Initializing Panda Motors 3D Showroom...")

    app = PandaMotorsApp(headless=args.headless)

    if args.zone:
        app.enter_showroom()
        app.nav_service.travel_to_zone(args.zone, smooth=False)

    if args.test_frames > 0:
        logger.info(f"Running automated frame test for {args.test_frames} frames...")
        for i in range(args.test_frames):
            app.taskMgr.step()
        logger.info("Automated frame test completed successfully!")
        app.destroy()
        sys.exit(0)

    logger.info("Starting main simulation loop...")
    app.run()


if __name__ == "__main__":
    main()
