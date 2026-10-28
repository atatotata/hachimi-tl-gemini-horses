"""Patch the hardcoded "Required Program Lv." label in resources.assets.

Hachimi's localize/text dictionaries cannot reach this label because it is
baked into the UI prefab. The replacement keeps the exact byte length, so the
serialized asset layout does not change.

Usage:
  python patch_required_lv.py --check
  python patch_required_lv.py --apply
  python patch_required_lv.py --restore
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

OLD = "必要演目Lv".encode("utf-8")
NEW = "Required Lv.  ".encode("utf-8")
EXPECTED = 3
DEFAULT_GAME_ROOT = Path(__file__).resolve().parents[3]
BACKUP_NAME = "resources.assets.bak_requiredlv"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--restore", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    asset = args.game_root / "UmamusumePrettyDerby_Jpn_Data" / "resources.assets"
    backup = asset.with_name(BACKUP_NAME)
    if not asset.exists():
        print(f"ERROR: asset not found: {asset}", file=sys.stderr)
        return 2

    if args.restore:
        if backup.exists():
            shutil.copy2(backup, asset)
            print(f"restored {asset} from {backup}")
            return 0
        data = asset.read_bytes()
        if data.count(NEW) != EXPECTED:
            print("ERROR: no backup and the patched marker is not present", file=sys.stderr)
            return 1
        tmp = asset.with_name(asset.name + ".restore_tmp")
        tmp.write_bytes(data.replace(NEW, OLD))
        os.replace(tmp, asset)
        print(f"reversed patch in {asset}")
        return 0

    data = asset.read_bytes()
    old_count = data.count(OLD)
    new_count = data.count(NEW)
    print(f"asset: {asset}")
    print(f"size: {len(data)}")
    print(f"sha256: {sha(data)}")
    print(f"old: {old_count}  new: {new_count}")

    if old_count == 0 and new_count == EXPECTED:
        print("already patched")
        return 0
    if old_count != EXPECTED:
        print(f"ERROR: expected {EXPECTED} original occurrences, found {old_count}", file=sys.stderr)
        return 1

    if args.check or not args.apply:
        print("dry run: no files written")
        return 0

    if not backup.exists():
        shutil.copy2(asset, backup)
        print(f"backup: {backup}")
    patched = data.replace(OLD, NEW)
    if len(patched) != len(data) or patched.count(NEW) != EXPECTED:
        print("ERROR: replacement changed the asset layout", file=sys.stderr)
        return 1
    tmp = asset.with_name(asset.name + ".patch_tmp")
    tmp.write_bytes(patched)
    os.replace(tmp, asset)
    print(f"applied: {asset}")
    print(f"sha256: {sha(patched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
