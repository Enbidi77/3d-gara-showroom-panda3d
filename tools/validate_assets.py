"""Asset validation script checking 3D models, textures, audio, and metadata."""

import json
import sys
from pathlib import Path


def validate():
    root = Path(__file__).resolve().parent.parent
    errors = []
    warnings = []

    print("=== PANDA MOTORS ASSET VALIDATION ===")

    # 1. Check data files
    for data_file in ["data/vehicles.json", "data/showroom_zones.json"]:
        p = root / data_file
        if not p.exists():
            errors.append(f"Missing data file: {data_file}")
        else:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"[OK] {data_file} parsed ({len(data)} entries)")
            except Exception as e:
                errors.append(f"Invalid JSON in {data_file}: {e}")

    # 2. Check config files
    for cfg in ["config/app.toml", "config/graphics.toml", "config/controls.toml"]:
        p = root / cfg
        if not p.exists():
            errors.append(f"Missing config file: {cfg}")
        else:
            print(f"[OK] {cfg} exists")

    # 3. Check vehicles
    veh_path = root / "data" / "vehicles.json"
    if veh_path.exists():
        with open(veh_path, "r", encoding="utf-8") as f:
            vehs = json.load(f)
            for v in vehs:
                ap = root / v["asset_path"]
                if not ap.exists():
                    warnings.append(f"Vehicle {v['id']} asset missing: {v['asset_path']} (procedural fallback will be used)")
                else:
                    print(f"[OK] Vehicle model {v['id']}: {v['asset_path']} ({ap.stat().st_size:,} bytes)")

    # 4. Check textures
    textures = [
        "assets/textures/marble/marble_01_diff_1k.jpg",
        "assets/textures/env/skyline_panorama.jpg",
        "assets/textures/ui/panda_wall_sign.png",
    ]
    for tex in textures:
        p = root / tex
        if not p.exists():
            warnings.append(f"Texture missing: {tex}")
        else:
            print(f"[OK] Texture: {tex} ({p.stat().st_size:,} bytes)")

    # 5. Check audio
    audios = [
        "assets/audio/ambient_showroom.wav",
        "assets/audio/ui_click.wav",
        "assets/audio/car_engine.wav",
        "assets/audio/footstep.wav",
    ]
    for a in audios:
        p = root / a
        if not p.exists():
            warnings.append(f"Audio missing: {a}")
        else:
            print(f"[OK] Audio: {a} ({p.stat().st_size:,} bytes)")

    print("\n--- Summary ---")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print("  -", w)
    if errors:
        print(f"Errors ({len(errors)}):")
        for err in errors:
            print("  -", err)
        sys.exit(1)
    else:
        print("ALL ASSETS AND CONFIGURATIONS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    validate()
