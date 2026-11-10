"""Optional convenience fetcher: downloads official PlantVillage metadata/repository only.

It intentionally does not substitute a mirror for the licensed Mendeley image archive.
"""
import argparse, subprocess
from pathlib import Path
REPO = "https://github.com/spMohanty/PlantVillage-Dataset.git"
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--destination", type=Path, default=Path("reference/PlantVillage-Dataset")); args = ap.parse_args()
    if args.destination.exists(): raise SystemExit(f"Already exists: {args.destination}")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", REPO, str(args.destination)], check=True)
    print("Metadata/source repository fetched. Download licensed color images manually as documented in metadata/SOURCE_ACQUISITION.md.")
