"""Merge translated 2026-10-24 scenario storytimelines into repo schema.

The extractor already drops engine block 0 (Hachimi does the same), so the
resulting text_block_list matches repo indices, including choices and color
spans. Writes 42-column wrapped text and LF newlines.

Usage:
  python merge_scenario_stories.py --dry-run
  python merge_scenario_stories.py --apply [--live] [--overwrite]
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
SRC_DEFAULT = Path(r"E:\AI_Offload\TMP\opencode\new_scenario_fetch\story_json")
WORK_DEFAULT = Path(r"E:\AI_Offload\TMP\opencode\new_scenario_fetch\work")
LIVE = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\hachimi\localized_data_1")
TEXT_DICT_DEFAULT = REPO / "localized_data" / "text_data_dict.json"

TAG_RE = re.compile(r"<[^>]+>")
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

# Canonical terms fixed after the first master pass.
REPLACEMENTS = [
    ("Uma-shiki Shundaisai", "Goshiki Shuntaisai"),
    ("Uma Shundaisai", "Goshiki Shuntaisai"),
    ("Goshiki Shundaisai", "Goshiki Shuntaisai"),
    ("Shunsai Grand Festival", "Goshiki Shuntaisai"),
    ("Shunsai", "Shuntaisai"),
    ("Shundaisai", "Shuntaisai"),
    ("Grand Horse Festival Camp", "Shuntaisai Camp"),
    ("Grand Horse Festival Scenario", "Goshiki Shuntaisai Scenario"),
    ("Grand Horse Festival", "Goshiki Shuntaisai"),
    ("Shundai Festival", "Shuntaisai"),
    ("Ryouran Enbu: Resplendent Dance of Bonds", "Resplendent Bond Dance"),
    ("Ryouran Enbu", "Resplendent Bond Dance"),
    ("Grand Festival Camp", "Shuntaisai Camp"),
    ("Performance Practice", "Program Rehearsal"),
    ("Program Practices", "Program Rehearsal"),
    ("Program Leads", "Performance Leads"),
    ("Designated members", "Performance Leads"),
    ("Sacred Banner Battle", "Sacred Flag Contest"),
    ("Sacred Banner Contest", "Sacred Flag Contest"),
    ("Sacred Banner Skirmish", "Sacred Flag Contest"),
    ("Sacred Banner Scramble", "Sacred Flag Contest"),
    ("Sacred Flag Scramble", "Sacred Flag Contest"),
    ("Dedicated Dance", "Votive Dance"),
    ("Dedication Dance", "Votive Dance"),
    ("Great Mikoshi Haul", "Grand Mikoshi Haul"),
    ("Grand Mikoshi Pull", "Grand Mikoshi Haul"),
    ("Grand Palanquin Haul", "Grand Mikoshi Haul"),
    ("Leaping Sprint", "Soaring Gallop"),
    ("Flight Sprint", "Soaring Gallop"),
    ("Steeplechase", "Soaring Gallop"),
    ("Hiku Preservation Society", "Soaring Gallop Preservation Society"),
    ("Hiku Preservation Association", "Soaring Gallop Preservation Association"),
    ("Hiku", "Soaring Gallop"),
    ("Lore Impartations", "Teaching Impartations"),
    ("Lore Transmutations", "Teaching Transmutations"),
    ("Tactful Grace", "Smooth Move"),
    ("Supreme Bow Draw", "Peerless Draw"),
    ("Giving My All", "Every Last Drop"),
    ("Arcing Ahead", "Carving the Arc"),
    ("Call from Afar", "Call from Beyond"),
    ("Extra Practice", "Extra Rehearsal"),
    ("Specialty Rate Up", "Specialty Priority Up"),
    ("Pacesetter", "Front Runner"),
    ("History Unveiled", "History Unraveled"),
    ("Azuma's Bond Increased", "Azuma's Evaluation Up"),
]


def display_width(text: str) -> int:
    width = 0
    for ch in TAG_RE.sub("", text):
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def wrap_paragraph(text: str, max_cols: int = 42) -> str:
    paras = (text or "").split("\n")
    result = []
    for para in paras:
        if not para:
            result.append("")
            continue
        if display_width(para) <= max_cols:
            result.append(para)
            continue
        parts = re.split(r"(<[^>]+>|\s+)", para)
        lines, current, current_w = [], "", 0
        for part in parts:
            if not part:
                continue
            if TAG_RE.match(part):
                current += part
                continue
            pw = display_width(part)
            if current_w + pw <= max_cols:
                current += part
                current_w += pw
            else:
                if current.rstrip():
                    lines.append(current.rstrip())
                current = part.lstrip()
                current_w = display_width(current)
        if current.rstrip():
            lines.append(current.rstrip())
        result.extend(lines)
    return " \n".join(result)


def clean_newlines(text: str) -> str:
    return text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n")


def canon(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SRC_DEFAULT)
    ap.add_argument("--work-dir", type=Path, default=WORK_DEFAULT)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--text-dict", type=Path, default=TEXT_DICT_DEFAULT)
    args = ap.parse_args()

    checkpoint_path = args.checkpoint or (args.work_dir / "newstories_checkpoint.json")
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    text_dict = json.loads(args.text_dict.read_text(encoding="utf-8"))
    cat181 = text_dict.get("181", {})
    files = sorted(args.source.rglob("storytimeline_*.json"))
    print(f"checkpoint={len(checkpoint)} source_files={len(files)}")

    missing: list[str] = []
    written = 0
    for src in files:
        data = json.loads(src.read_text(encoding="utf-8"))
        key = src.stem.replace("storytimeline_", "")
        out = dict(data)
        out["no_wrap"] = True

        title = out.get("title")
        if isinstance(title, str) and title.strip():
            tkey = f"{key}__T"
            if key in cat181 and cat181[key].strip():
                out["title"] = cat181[key]
            elif tkey in checkpoint:
                out["title"] = canon(clean_newlines(checkpoint[tkey]))
            elif JP_RE.search(title):
                missing.append(tkey)

        for i, block in enumerate(out.get("text_block_list", [])):
            text = block.get("text", "")
            bkey = f"{key}__B{i}"
            if bkey in checkpoint:
                block["text"] = wrap_paragraph(canon(clean_newlines(checkpoint[bkey])))
            elif isinstance(text, str) and text.strip():
                if JP_RE.search(text):
                    missing.append(bkey)
                else:
                    block["text"] = clean_newlines(text)

            name = block.get("name")
            nkey = f"{key}__N{i}"
            if nkey in checkpoint:
                block["name"] = clean_newlines(checkpoint[nkey])
            elif isinstance(name, str) and name.strip() and JP_RE.search(name):
                missing.append(nkey)

            for j, choice in enumerate(block.get("choice_data_list", []) or []):
                ckey = f"{key}__C{i}_{j}"
                if ckey in checkpoint:
                    block["choice_data_list"][j] = wrap_paragraph(
                        canon(clean_newlines(checkpoint[ckey]))
                    )
                elif isinstance(choice, str) and choice.strip() and JP_RE.search(choice):
                    missing.append(ckey)

            for j, color in enumerate(block.get("color_text_info_list", []) or []):
                if not isinstance(color, dict):
                    continue
                ctext = color.get("Text")
                xkey = f"{key}__X{i}_{j}"
                if xkey in checkpoint:
                    color["Text"] = canon(clean_newlines(checkpoint[xkey]))
                elif isinstance(ctext, str) and ctext.strip() and JP_RE.search(ctext):
                    missing.append(xkey)

            if block.get("color_text_info_list"):
                block["color_text_info_list"] = [
                    c.get("Text") if isinstance(c, dict) else c
                    for c in block["color_text_info_list"]
                ]

        rel = src.relative_to(args.source)
        dests = [REPO / "localized_data" / "assets" / "story" / "data" / rel]
        if args.live:
            dests.append(LIVE / "assets" / "story" / "data" / rel)

        for dest in dests:
            if dest.exists() and not args.overwrite:
                missing.append(f"{key}__EXISTS:{dest}")
                continue
            if args.apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(
                    json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                written += 1

    print(f"written={written} missing_items={len(missing)}")
    if missing:
        for item in missing[:20]:
            print("MISSING", item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
