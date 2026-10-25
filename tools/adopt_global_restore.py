#!/usr/bin/env python3
"""Restore and adopt official Global text_data on Flagship branches.

The Oct 22 UmaTL sync overwrote roughly 24k rows that already matched
Global.  This script puts those rows back from the last known-good snapshot
(``ed2049cd5``), then adds JP-backed Global rows that are still missing.

Rules
-----
* Only keys present in the JP master are considered. Global-only rows are
  skipped because the JP client has no matching text.
* cat48 is never touched; SD skill math wins.
* A row is restored only when the old repo value matched the current Global
  value after normalising line breaks and ``$(scale NN)`` tags. That keeps
  later manual fixes (skills, traits, conditions, titles) intact.
* Missing rows are added from Global with literal ``\\n`` converted to real
  newlines.
* cat63/index 61 is skipped: Global replaced that tutorial row with a
  different event's story.

Usage
-----
  python tools/adopt_global_restore.py --dry-run
  python tools/adopt_global_restore.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEXT_PATH = REPO / "localized_data" / "text_data_dict.json"
LIVE_PATH = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn"
    r"\hachimi\localized_data_1\text_data_dict.json"
)
GLOBAL_MASTER = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby"
    r"\UmamusumePrettyDerby_Data\Persistent\master\master.mdb"
)
JP_MASTER = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn"
    r"\UmamusumePrettyDerby_Jpn_Data\Persistent\master\master.mdb"
)
BASELINE = "ed2049cd5"
FLAGSHIP = {"main", "full", "full-slim"}
SKIP = {("63", "61")}
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
SCALE_RE = re.compile(r"^\$\(scale \d+\)\s*")


def clean(text: str) -> str:
    return (
        str(text)
        .replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\r\n", "\n")
    )


def norm(text: str) -> str:
    text = SCALE_RE.sub("", clean(text))
    return re.sub(r"\s+", " ", text).strip()


def branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO,
            text=True,
        ).strip()
    except Exception:
        return ""


def load_global() -> dict[str, dict[str, str]]:
    conn = sqlite3.connect(str(GLOBAL_MASTER))
    rows = conn.execute(
        "SELECT category, [index], text FROM text_data"
    ).fetchall()
    conn.close()
    out: dict[str, dict[str, str]] = {}
    for cat, idx, text in rows:
        if not text or not str(text).strip():
            continue
        out.setdefault(str(cat), {})[str(idx)] = str(text)
    return out


def jp_keys() -> set[tuple[str, str]]:
    conn = sqlite3.connect(str(JP_MASTER))
    rows = conn.execute("SELECT category, [index] FROM text_data").fetchall()
    conn.close()
    return {(str(c), str(i)) for c, i in rows}


def load_baseline(ref: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{ref}:localized_data/text_data_dict.json"],
        cwd=REPO,
    )
    return json.loads(raw)


def write_dict(path: Path, data: dict) -> None:
    trailing = path.read_bytes().endswith(b"\n") if path.exists() else True
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        if trailing:
            f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the repo and live mirror")
    parser.add_argument("--dry-run", action="store_true", help="show the plan only (default)")
    parser.add_argument("--baseline", default=BASELINE, help="known-good git ref")
    parser.add_argument("--no-live", action="store_true", help="write only the repo")
    parser.add_argument(
        "--allow-umatl",
        action="store_true",
        help="allow running on a non-Flagship branch (experiments only)",
    )
    args = parser.parse_args()

    if args.apply and args.dry_run:
        parser.error("choose --apply or --dry-run, not both")
    if not args.apply:
        args.dry_run = True

    current = branch()
    if current not in FLAGSHIP and not args.allow_umatl:
        parser.error(
            f"branch {current!r} is not Flagship; "
            "use --allow-umatl only for a deliberate experiment"
        )

    repo = json.loads(TEXT_PATH.read_text(encoding="utf-8"))
    baseline = load_baseline(args.baseline)
    glob = load_global()
    jp = jp_keys()

    restore: dict[tuple[str, str], str] = {}
    add: dict[tuple[str, str], str] = {}
    review: list[tuple[str, str, str, str]] = []
    counts = {"matched": 0, "restore": 0, "add": 0, "review": 0, "global_only": 0}

    for cat, rows in glob.items():
        if cat == "48":
            continue
        for idx, text in rows.items():
            key = (cat, idx)
            if key in SKIP:
                continue
            if JP_RE.search(text):
                continue
            if key not in jp:
                counts["global_only"] += 1
                continue
            current_val = repo.get(cat, {}).get(idx)
            if current_val is None:
                add[key] = clean(text)
                counts["add"] += 1
                continue
            if norm(current_val) == norm(text):
                counts["matched"] += 1
                continue
            old_val = baseline.get(cat, {}).get(idx)
            if old_val is not None and norm(old_val) == norm(text):
                restore[key] = old_val
                counts["restore"] += 1
            else:
                counts["review"] += 1
                if len(review) < 12:
                    review.append((cat, idx, current_val, clean(text)))

    print(f"branch: {current}")
    print(f"baseline: {args.baseline}")
    print(f"Global rows: {sum(len(v) for v in glob.values()):,}")
    for k in ("matched", "restore", "add", "review", "global_only"):
        print(f"  {k:12}: {counts[k]:,}")

    restore_by_cat: dict[str, int] = {}
    for cat, _ in restore:
        restore_by_cat[cat] = restore_by_cat.get(cat, 0) + 1
    print("  restore top:", sorted(restore_by_cat.items(), key=lambda x: -x[1])[:10])
    print("  add top:", sorted(
        ((c, sum(1 for k in add if k[0] == c)) for c in {k[0] for k in add}),
        key=lambda x: -x[1],
    )[:10])
    for cat, idx, cur, new in review:
        print(f"  review {cat}/{idx}: {cur[:60]!r} -> {new[:60]!r}")

    if args.dry_run:
        print("dry run: no files written")
        return 0

    if not LIVE_PATH.exists() and not args.no_live:
        parser.error(f"live mirror not found: {LIVE_PATH}")

    live = None if args.no_live else json.loads(LIVE_PATH.read_text(encoding="utf-8"))

    def apply_to(data: dict) -> None:
        for (cat, idx), value in restore.items():
            data.setdefault(cat, {})[idx] = value
        for (cat, idx), value in add.items():
            data.setdefault(cat, {})[idx] = value

    before_cat48 = json.dumps(repo.get("48", {}), sort_keys=True)
    apply_to(repo)
    if live is not None:
        apply_to(live)

    if live is not None:
        backup = LIVE_PATH.with_suffix(LIVE_PATH.suffix + ".bak_global_restore")
        shutil.copy2(LIVE_PATH, backup)
        print(f"  live backup: {backup}")

    write_dict(TEXT_PATH, repo)
    if live is not None:
        write_dict(LIVE_PATH, live)

    after_cat48 = json.dumps(repo.get("48", {}), sort_keys=True)
    assert before_cat48 == after_cat48, "cat48 changed"

    changed = list(restore.values()) + list(add.values())
    leaks = [v for v in changed if JP_RE.search(v)]
    if leaks:
        print(f"ERROR: {len(leaks)} Japanese values in the change set", file=sys.stderr)
        return 1

    print(f"wrote {len(restore):,} restored and {len(add):,} added rows")
    print("cat48 unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
