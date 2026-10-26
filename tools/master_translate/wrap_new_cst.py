"""Reflow newly translated character_system_text lines into <=3 lines.

Only touches the 53 CST keys listed in master_untranslated.json. Tries 100%
down to 70% width and adds $(scale NN) when needed. One overlong line is
manually tightened rather than shrunk below 80%.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses")
DUMP = REPO / "tools" / "master_translate" / "master_untranslated.json"
CST = REPO / "localized_data" / "character_system_text_dict.json"
LIVE = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\hachimi\localized_data_1\character_system_text_dict.json")

TAG_RE = re.compile(r"<[^>]+>")
SCALE_RE = re.compile(r"^\$\(scale\s+\d+\)")

FIXUPS = {
    "cst_1009_90211": (
        "Look at that sleepy face... Ugh, seriously?\n"
        "I woke up early to put on this kimono...\n"
        "Hmph, try following my example for once!"
    ),
}


def width(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        for ch in TAG_RE.sub("", text)
    )


def wrap_words(text: str, cols: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if width(candidate) <= cols:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    dump = json.loads(DUMP.read_text(encoding="utf-8"))
    cst = json.loads(CST.read_text(encoding="utf-8"))
    changed = 0
    for entry in dump["entries"]:
        if entry["type"] != "cst":
            continue
        cid = str(entry["character_id"])
        vid = str(entry["voice_id"])
        text = cst.get(cid, {}).get(vid)
        if not isinstance(text, str) or not text.strip():
            continue
        if SCALE_RE.match(text):
            continue
        if entry["id"] in FIXUPS:
            text = FIXUPS[entry["id"]]
        lines = text.split("\n")
        if len(lines) <= 3 and max(width(line) for line in lines) <= 42:
            continue
        plain = " ".join(text.split())
        chosen = None
        for pct in (100, 95, 90, 85, 80, 75, 70):
            candidate = wrap_words(plain, int(42 * 100 / pct))
            if len(candidate) <= 3:
                chosen = (pct, candidate)
                break
        if chosen is None:
            chosen = (70, wrap_words(plain, int(42 * 100 / 70)))
        pct, candidate = chosen
        value = "\n".join(candidate)
        if pct < 100:
            value = f"$(scale {pct}){value}"
        cst[cid][vid] = value
        changed += 1
        print(f"{entry['id']} {pct}% {len(candidate)} lines max={max(width(x) for x in candidate)}")

    print(f"changed={changed}")
    out = json.dumps(cst, ensure_ascii=False, indent=2) + "\n"
    CST.write_text(out, encoding="utf-8", newline="\n")
    if args.live:
        LIVE.write_text(out, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
