"""Verify the prepared directory and provenance index before model training."""
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path
import yaml

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--dataset",type=Path,default=Path("dataset")); ap.add_argument("--config",type=Path,default=Path("config/classes.yaml")); a=ap.parse_args()
    cfg=yaml.safe_load(a.config.read_text()); expected=set(cfg["classes"]); rows=[]
    with (a.dataset/"image_index.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
    errors=[]
    if not rows: errors.append("image_index.csv has no records")
    seen={}
    for row in rows:
        p=Path(row["destination"])
        if row["target_class"] not in expected or row["split"] not in cfg["splits"]: errors.append(f"bad label/split: {row}"); continue
        if not p.is_file(): errors.append(f"missing: {p}"); continue
        actual=digest(p)
        if actual != row["sha256"]: errors.append(f"checksum mismatch: {p}")
        if actual in seen and seen[actual] != row["split"]: errors.append(f"leakage: {p} duplicates {seen[actual]}")
        seen[actual]=row["split"]
    for split in cfg["splits"]:
        missing=expected-{p.name for p in (a.dataset/split).iterdir() if p.is_dir()} if (a.dataset/split).exists() else expected
        if missing: errors.append(f"{split} missing class folders: {sorted(missing)}")
    print(json.dumps({"records":len(rows),"by_split_class":Counter((r["split"],r["target_class"]) for r in rows),"errors":errors},default=str,indent=2))
    if errors: raise SystemExit(1)
