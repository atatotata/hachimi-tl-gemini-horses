#!/usr/bin/env python3
"""Fail if localize_dict.json or story/home timeline files contain literal backslash-n.

Hachimi localize + timeline renderers need REAL newlines (char U+000A).
text_data_dict / character_system_text_dict / race_jikkyo / lyrics intentionally
keep the game-master literal backslash-n format and are NOT checked here.

Usage:
  python tools/master_translate/guard_literal_newlines.py          # check, exit 1 on fail
  python tools/master_translate/guard_literal_newlines.py --fix    # convert in place
"""
import json
import sys
import pathlib
import re

BS = chr(92)
LIT = BS + "n"
# one backslash + n, NOT preceded by another backslash
PAT = re.compile(r"(?<!" + BS + BS + r")" + re.escape(LIT))

REPO = pathlib.Path(__file__).resolve().parents[2]
LD = REPO / "localized_data"
FIX = "--fix" in sys.argv


def str_has_lit(o):
    if isinstance(o, dict):
        return any(str_has_lit(v) for v in o.values())
    if isinstance(o, list):
        return any(str_has_lit(v) for v in o)
    if isinstance(o, str):
        return bool(PAT.search(o))
    return False


def convert_obj(o):
    if isinstance(o, dict):
        return {k: convert_obj(v) for k, v in o.items()}
    if isinstance(o, list):
        return [convert_obj(v) for v in o]
    if isinstance(o, str):
        return PAT.sub("\n", o)
    return o


def write_preserve(p, data):
    ends_nl = p.read_bytes().endswith(b"\n")
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    if ends_nl:
        txt += "\n"
    p.write_text(txt, encoding="utf-8", newline="\n")


failures = []
targets = []

p = LD / "localize_dict.json"
targets.append(p)

for base in [LD / "assets/story/data", LD / "assets/home"]:
    if base.exists():
        targets.extend(sorted(base.rglob("*.json")))

for p in targets:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"{p}: JSON parse error: {e}")
        continue
    if str_has_lit(d):
        if FIX:
            write_preserve(p, convert_obj(d))
            print(f"fixed {p.relative_to(LD)}")
        else:
            try:
                rel = p.relative_to(LD)
            except ValueError:
                rel = p
            failures.append(str(rel))

if failures and not FIX:
    print("FAIL: literal backslash-n detected (must be real newlines U+000A):")
    for x in failures[:30]:
        print("  " + x)
    if len(failures) > 30:
        print(f"  ... and {len(failures) - 30} more")
    print("Fix: python tools/master_translate/guard_literal_newlines.py --fix")
    sys.exit(1)

if FIX:
    print("fix complete")
else:
    print("OK: no literal backslash-n in localize_dict or story/home timelines")
