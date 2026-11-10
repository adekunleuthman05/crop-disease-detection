"""Create a provenance-preserving 11-class dataset from manually acquired sources.

Run from package root. Input images are never resized/augmented/cropped here.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, random, re, shutil
from collections import defaultdict
from pathlib import Path
import imagehash, yaml
from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
SKIP_TOKENS = {"augment", "augmented", "augmentation", "gray", "grayscale", "segment", "segmented"}

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def image_phash(path: Path) -> str:
    with Image.open(path) as im:
        return str(imagehash.phash(im.convert("RGB")))

def image_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
            yield p

def find_class_files(source_root: Path, label: str):
    """Match the closest folder whose normalized name equals the source label."""
    matches = [p for p in source_root.rglob("*") if p.is_dir() and norm(p.name) == norm(label)]
    candidates = []
    for folder in matches:
        if any(token in norm(str(folder.relative_to(source_root))) for token in SKIP_TOKENS):
            continue
        files = list(image_files(folder))
        if files:
            candidates.append((folder, files))
    if not candidates:
        raise FileNotFoundError(f"No non-augmented folder matching {label!r} under {source_root}")
    # Nested class folders can duplicate the same content; choose the largest only if unique.
    largest = max(len(files) for _, files in candidates)
    winners = [(folder, files) for folder, files in candidates if len(files) == largest]
    if len(winners) != 1:
        raise RuntimeError(f"Ambiguous folders for {label!r}: {[str(x[0]) for x in winners]}")
    return winners[0]

def allocate(n: int, fractions: dict[str, float]):
    raw = {k: n * v for k, v in fractions.items()}
    result = {k: int(v) for k, v in raw.items()}
    for key, _ in sorted(raw.items(), key=lambda kv: (kv[1] - int(kv[1]), kv[0]), reverse=True)[:n - sum(result.values())]:
        result[key] += 1
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("raw"))
    ap.add_argument("--output", type=Path, default=Path("dataset"))
    ap.add_argument("--config", type=Path, default=Path("config/classes.yaml"))
    ap.add_argument("--report", type=Path, default=Path("metadata/preparation_report.json"))
    ap.add_argument("--near-distance", type=int, default=4, help="pHash Hamming distance; 0 disables near-duplicate comparison")
    ap.add_argument("--copy", action="store_true", help="Copy instead of hard-linking selected originals")
    args = ap.parse_args()
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"Refusing to mix outputs: {args.output} is not empty. Choose a new --output.")
    args.output.mkdir(parents=True, exist_ok=True)
    inventory, hashes, phashes, source_folders = [], {}, [], {}
    for target, spec in cfg["classes"].items():
        folder, files = find_class_files(args.raw / spec["source"], spec["source_class"])
        source_folders[target] = str(folder)
        for p in sorted(files):
            try:
                digest, perceptual = sha256(p), image_phash(p)
            except (UnidentifiedImageError, OSError) as exc:
                inventory.append({"status":"unreadable", "path":str(p), "error":str(exc), "target_class":target})
                continue
            record = {"path":str(p), "target_class":target, "source_id":spec["source"], "sha256":digest, "phash":perceptual}
            inventory.append(record); hashes.setdefault(digest, []).append(record); phashes.append(record)
    exact_dupes = [v for v in hashes.values() if len(v) > 1]
    cross_class = [v for v in exact_dupes if len({x["target_class"] for x in v}) > 1]
    if cross_class:
        raise SystemExit("Exact duplicate appears in different target classes; resolve labels before splitting.")
    keep = {x["path"] for x in inventory if "sha256" in x}
    for group in exact_dupes:
        for duplicate in group[1:]: keep.discard(duplicate["path"])
    near_pairs = []
    kept_records = [x for x in inventory if x.get("path") in keep]
    if args.near_distance:
        for i, a in enumerate(kept_records):
            for b in kept_records[i + 1:]:
                distance = imagehash.hex_to_hash(a["phash"]) - imagehash.hex_to_hash(b["phash"])
                if distance <= args.near_distance:
                    near_pairs.append({"a":a["path"],"b":b["path"],"distance":distance,"same_class":a["target_class"] == b["target_class"]})
        # Remove only same-class near duplicates; cross-class pairs are retained and reported for review.
        for pair in near_pairs:
            if pair["same_class"]: keep.discard(pair["b"])
    selected = [x for x in inventory if x.get("path") in keep]
    randomizer = random.Random(cfg["seed"])
    records = []
    for target in cfg["classes"]:
        rows = [x for x in selected if x["target_class"] == target]
        randomizer.shuffle(rows); counts = allocate(len(rows), cfg["splits"]); offset = 0
        for split in cfg["splits"]:
            for row in rows[offset:offset + counts[split]]:
                original = Path(row["path"]); name = f"{row['sha256'][:16]}{original.suffix.lower()}"
                destination = args.output / split / target / name; destination.parent.mkdir(parents=True, exist_ok=True)
                if args.copy: shutil.copy2(original, destination)
                else: destination.hardlink_to(original)
                records.append({**row, "split":split, "destination":str(destination)})
            offset += counts[split]
    with (args.output / "image_index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id","target_class","split","sha256","phash","path","destination"])
        writer.writeheader(); writer.writerows(records)
    report = {"seed":cfg["seed"], "splits":cfg["splits"], "source_folders":source_folders,
              "input_readable":sum("sha256" in x for x in inventory), "selected_originals":len(selected),
              "exact_duplicates_removed":sum(len(x)-1 for x in exact_dupes), "near_duplicate_pairs":near_pairs,
              "unreadable":[x for x in inventory if x.get("status") == "unreadable"],
              "counts":{s:{c:sum(r["split"]==s and r["target_class"]==c for r in records) for c in cfg["classes"]} for s in cfg["splits"]}}
    args.report.parent.mkdir(parents=True, exist_ok=True); args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["counts"], indent=2)); print(f"Prepared {len(records)} originals. Report: {args.report}")
if __name__ == "__main__": main()
