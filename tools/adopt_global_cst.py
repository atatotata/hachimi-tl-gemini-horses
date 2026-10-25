#!/usr/bin/env python3
"""Adopt official Global voice lines that still differ in wording.

Only rows whose wording differs after normalising line breaks/scale tags are
touched. Rows that differ only in wrapping are left alone, so the existing
11k-line rewrap stays intact.

New lines are wrapped to 42 display columns and at most 3 lines. If they do
not fit, the script tries 95, 90, 85, 80, 75, then 70 percent scaling.

Usage
-----
  python tools/adopt_global_cst.py --dry-run
  python tools/adopt_global_cst.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CST_PATH = REPO / "localized_data" / "character_system_text_dict.json"
LIVE_PATH = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn"
    r"\hachimi\localized_data_1\character_system_text_dict.json"
)
GLOBAL_MASTER = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby"
    r"\UmamusumePrettyDerby_Data\Persistent\master\master.mdb"
)
JP_MASTER = Path(
    r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn"
    r"\UmamusumePrettyDerby_Jpn_Data\Persistent\master\master.mdb"
)
FLAGSHIP = {"main", "full", "full-slim"}
PCTS = [100, 95, 90, 85, 80, 75, 70]
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
SCALE_RE = re.compile(r"^\$\(scale \d+\)\s*")
TAG_RE = re.compile(r"<[^>]+>|\$\([^)]*\)")
FIXUPS = {
    ("1099", "91010"): [("sp I'm", "so I'm")],
}


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


def display_width(text: str) -> int:
    text = TAG_RE.sub("", text)
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def wrap(text: str, cols: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = (line + " " + word).strip()
        if line and display_width(candidate) > cols:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO,
            text=True,
        ).strip()
    except Exception:
        return ""


def write_dict(path: Path, data: dict) -> None:
    trailing = path.read_bytes().endswith(b"\n") if path.exists() else True
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        if trailing:
            f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-live", action="store_true")
    parser.add_argument("--allow-umatl", action="store_true")
    args = parser.parse_args()

    if args.apply and args.dry_run:
        parser.error("choose --apply or --dry-run, not both")
    if not args.apply:
        args.dry_run = True

    sys.stdout.reconfigure(encoding="utf-8")
    current = branch()
    if current not in FLAGSHIP and not args.allow_umatl:
        parser.error(f"branch {current!r} is not Flagship")

    repo = json.loads(CST_PATH.read_text(encoding="utf-8"))
    conn_g = sqlite3.connect(str(GLOBAL_MASTER))
    global_rows = conn_g.execute(
        "SELECT character_id, voice_id, text FROM character_system_text"
    ).fetchall()
    conn_g.close()
    conn_j = sqlite3.connect(str(JP_MASTER))
    jp = {
        (str(c), str(v))
        for c, v in conn_j.execute(
            "SELECT character_id, voice_id FROM character_system_text"
        )
    }
    conn_j.close()

    changes: list[tuple[str, str, str, int, list[str]]] = []
    skipped: list[tuple[str, str, int]] = []
    for ch, vid, text in global_rows:
        key = (str(ch), str(vid))
        if not text or not str(text).strip() or JP_RE.search(str(text)):
            continue
        if key not in jp:
            continue
        old = repo.get(key[0], {}).get(key[1])
        if old is None:
            continue
        new = clean(text)
        for src, dst in FIXUPS.get(key, []):
            new = new.replace(src, dst)
        if norm(old) == norm(new):
            continue

        chosen = None
        for pct in PCTS:
            cols = int(42 * 100 / pct)
            lines = wrap(new, cols)
            if len(lines) <= 3:
                chosen = (pct, lines)
                break
        if chosen is None:
            skipped.append((key[0], key[1], len(new)))
            continue

        pct, lines = chosen
        body = "\n".join(lines)
        if pct < 100:
            body = f"$(scale {pct})" + body
        changes.append((key[0], key[1], body, pct, lines))

    print(f"branch: {current}")
    print(f"Global cst rows: {len(global_rows):,}")
    print(f"  wording changes: {len(changes):,}")
    print(f"  skipped (>3 lines even at 70%): {len(skipped):,}")
    for cid, vid, body, pct, lines in changes[:6]:
        print(f"  {cid}/{vid} at {pct}%: {body.replace(chr(10), ' / ')}")
    for cid, vid, length in skipped[:6]:
        print(f"  skip {cid}/{vid}: {length} chars")

    if args.dry_run:
        print("dry run: no files written")
        return 0

    if not LIVE_PATH.exists() and not args.no_live:
        parser.error(f"live mirror not found: {LIVE_PATH}")
    live = None if args.no_live else json.loads(LIVE_PATH.read_text(encoding="utf-8"))

    def apply_to(data: dict) -> None:
        for cid, vid, body, _, _ in changes:
            data.setdefault(cid, {})[vid] = body

    apply_to(repo)
    if live is not None:
        apply_to(live)
        backup = LIVE_PATH.with_suffix(LIVE_PATH.suffix + ".bak_global_restore")
        shutil.copy2(LIVE_PATH, backup)
        print(f"  live backup: {backup}")

    for cid, vid, body, pct, lines in changes:
        if JP_RE.search(body):
            print(f"ERROR: Japanese text at {cid}/{vid}", file=sys.stderr)
            return 1
        cols = int(42 * 100 / pct)
        if any(display_width(line) > cols for line in lines):
            print(f"ERROR: line too wide at {cid}/{vid}", file=sys.stderr)
            return 1

    write_dict(CST_PATH, repo)
    if live is not None:
        write_dict(LIVE_PATH, live)

    print(f"wrote {len(changes):,} voice lines")
    for key in (("9001", "250000"), ("9001", "250001")):
        print(f"PINNED_CST[{key}] = {repo[key[0]][key[1]]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
