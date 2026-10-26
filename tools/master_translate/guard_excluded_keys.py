"""Guard: keep Error-102 keys out of localize_dict.json.

Run before any translation batch, sync, or release:
  python guard_excluded_keys.py            # dry run
  python guard_excluded_keys.py --fix      # remove from repo + live mirror
  python guard_excluded_keys.py --ci       # fail if present or list changed

The canonical list is pinned below. If excluded_keys.json is edited, this
guard fails even when the localize dictionary happens to be clean.
"""
import argparse
import json
import os
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
EXCLUDED_PATH = SCRIPT_DIR / "excluded_keys.json"
LOCALIZE_PATH = REPO_ROOT / "localized_data" / "localize_dict.json"
MIRROR_PATH = pathlib.Path(
    os.environ.get(
        "HACHIMI_LOCALIZE",
        r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn"
        r"\hachimi\localized_data_1\localize_dict.json",
    )
)

EXPECTED_KEYS = {
    "SingleMode418025",
    "SingleMode418026",
    "SingleMode418027",
    "SingleMode418028",
    "SingleMode418029",
    "SingleMode418030",
    "SingleMode418031",
    "SingleMode418032",
    "SingleMode418033",
    "SingleMode418034",
    "SingleMode418035",
    "SingleMode418036",
    "SingleMode418037",
}


def canonical_keys() -> set[str] | None:
    """Load the exclusion list and verify it matches the pinned set."""
    try:
        data = json.loads(EXCLUDED_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {EXCLUDED_PATH}: {exc}", file=sys.stderr)
        return None
    keys = set(data.get("localize_dict", []))
    if keys != EXPECTED_KEYS:
        missing = sorted(EXPECTED_KEYS - keys)
        extra = sorted(keys - EXPECTED_KEYS)
        print("ERROR: excluded_keys.json no longer matches the canonical list.", file=sys.stderr)
        if missing:
            print(f"  missing: {', '.join(missing)}", file=sys.stderr)
        if extra:
            print(f"  extra:   {', '.join(extra)}", file=sys.stderr)
        return None
    return keys


def check_path(label: str, path: pathlib.Path, keys: set[str], fix: bool) -> int:
    if not path.exists():
        print(f"  {label}: {path} not found, skipping")
        return 0
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    present = [k for k in keys if k in data]
    if not present:
        print(f"  {label}: clean ({len(data)} keys, 0 excluded)")
        return 0
    if not fix:
        print(f"  {label}: {len(present)} EXCLUDED KEYS PRESENT")
        for key in present:
            print(f"    {key} = {repr(data[key])[:80]}")
        return len(present)
    for key in present:
        del data[key]
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  {label}: removed {len(present)} excluded keys -> {len(data)} remaining")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="remove keys from repo and mirror")
    parser.add_argument("--ci", action="store_true", help="read-only check; fail on any issue")
    args = parser.parse_args()
    if args.fix and args.ci:
        parser.error("--fix and --ci cannot be used together")

    keys = canonical_keys()
    if keys is None:
        return 1

    bad = check_path("repo", LOCALIZE_PATH, keys, args.fix)
    if not args.ci:
        bad += check_path("mirror", MIRROR_PATH, keys, args.fix)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
