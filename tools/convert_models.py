"""Model converter utility supporting GLB/glTF to Panda3D BAM conversion."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def convert_file(src_path: Path, dst_path: Path) -> bool:
    print(f"Converting {src_path} -> {dst_path}...")
    try:
        res = subprocess.run(["gltf2bam", str(src_path), str(dst_path)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[SUCCESS] Converted {dst_path.name} ({dst_path.stat().st_size:,} bytes)")
            return True
        else:
            print(f"[WARN] gltf2bam returned code {res.returncode}. Attempting Blender normalization...")
            import bpy
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(src_path))
            temp_clean = src_path.parent / f"_temp_clean_{src_path.name}"
            bpy.ops.export_scene.gltf(filepath=str(temp_clean), export_format="GLB")
            res2 = subprocess.run(["gltf2bam", str(temp_clean), str(dst_path)], capture_output=True, text=True)
            if temp_clean.exists():
                os.remove(temp_clean)
            if res2.returncode == 0:
                print(f"[SUCCESS] Converted via Blender cleanup: {dst_path.name}")
                return True
            else:
                print(f"[ERROR] Failed to convert: {res2.stderr}")
                return False
    except Exception as e:
        print(f"[ERROR] Exception during conversion: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Panda Motors 3D Model Converter")
    parser.add_argument("src", help="Path to input 3D model (.glb, .gltf)")
    parser.add_argument("dst", nargs="?", default="", help="Optional output BAM path")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"Source file not found: {src}")
        sys.exit(1)

    dst = Path(args.dst) if args.dst else src.with_suffix(".bam")
    success = convert_file(src, dst)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
