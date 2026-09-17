"""Guard: strip excluded keys from localize_dict.json.

Run before any translation batch or sync to prevent Error 102.
Usage: python guard_excluded_keys.py [--fix]

Without --fix: reports which excluded keys are present (dry run).
With --fix: removes them from localize_dict.json and reports.
"""
import json, sys, pathlib

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXCLUDED_PATH = SCRIPT_DIR / "excluded_keys.json"
LOCALIZE_PATH = pathlib.Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\localized_data\localize_dict.json")
LOC7_PATH = pathlib.Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\hachimi\localized_data_7\localize_dict.json")

fix = "--fix" in sys.argv

with open(EXCLUDED_PATH, "r", encoding="utf-8") as f:
    excluded = json.load(f)

bad_keys = set(excluded.get("localize_dict", []))

for label, path in [("repo", LOCALIZE_PATH), ("loc7", LOC7_PATH)]:
    if not path.exists():
        print(f"  {label}: {path} not found, skipping")
        continue
    with open(path, "r", encoding="utf-8") as f:
        loc = json.load(f)
    present = [k for k in bad_keys if k in loc]
    if not present:
        print(f"  {label}: clean ({len(loc)} keys, 0 excluded)")
        continue
    if fix:
        for k in present:
            del loc[k]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(loc, f, ensure_ascii=False, indent=2)
        print(f"  {label}: removed {len(present)} excluded keys -> {len(loc)} remaining")
    else:
        print(f"  {label}: {len(present)} EXCLUDED KEYS PRESENT (dry run, use --fix to remove)")
        for k in present:
            print(f"    {k} = {repr(loc[k])[:80]}")
