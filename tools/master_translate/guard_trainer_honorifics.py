#!/usr/bin/env python3
"""
Guard against regressions that overwrite or drop character-specific trainer
honorifics and nicknames ("Tore-san", "Tore-kun", "Tore-chan", "Tore-sama",
"Tore-dono", "Tore-senpai", "Tore-pi", "Tore-cchi", "Teach", "Big Brother",
"Big Bro", "guinea pig", "Prez", "my liege", "my King", etc.).

Enforces five invariants:
1. No retired/forbidden trainer-nickname spellings appear anywhere in
   localized_data/*.json (dicts, story timelines, home timelines):
   - "Trainer-san / -sama / -chan / -kun / -dono / -senpai"
   - "Trai-pi / Trai-pippi / Trai-piii / Trai-chan / Train-pi / Trainer-pi"
   - "T-Rain / T-Rainster / T-Rain-pi / T-Rainppi / T-Rainyo / T-Rainpoyo"
   - "Trainy / Trainie / Trainey" (and hyphenated suffixes)
2. Sentinel rows in text_data_dict.json and character_system_text_dict.json
   retain their canonical character-specific trainer terms (so an unguarded
   Global overlay cannot silently revert Tore-pi -> T-Rain or Tore-san ->
   Trainer).
3. tools/voice_bible/uma_voice_bible.json and canonical_voice.py match the
   Tore- policy (default "Tore-san", 1065 -> "Tore-pi", 1080 -> "Tore-chan",
   1091 -> "Tore-cchi", 1012 -> "Teach", 1030 -> "Big Brother", 1038 ->
   "Big Bro", etc., and zero Trainer-san/-kun/-chan/-sama/-dono or T-Rain
   trainer_term values).
4. sync_umatl.py CANONICAL_NAMES and sync_global.py trainer-honorific
   protection remain wired in.

Exits non-zero if any violation is found. Safe to run in CI and locally.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
LD = REPO_ROOT / "localized_data"
BIBLE_PATH = REPO_ROOT / "tools" / "voice_bible" / "uma_voice_bible.json"
CANONICAL_VOICE_PATH = REPO_ROOT / "tools" / "voice_bible" / "canonical_voice.py"
SYNC_UMATL_PATH = REPO_ROOT / "sync_umatl.py"
SYNC_GLOBAL_PATH = REPO_ROOT / "sync_global.py"

# Retired / forbidden trainer-address tokens across all localized_data JSON files.
# Note: storytimeline_501031304.json contains 4 intentional player-choice
# gender-confusion lines ("Wait, Trainer-kun...?" / "Wait, Trainer-chan...?")
# and storytimeline_041069007.json contains Sakura Chiyono O's "Trainynotes!"
# pun; both are explicitly allowlisted in check_localized_data().
FORBIDDEN_TOKEN_RE = re.compile(
    r"\b(?:"
    r"Trainer-(?:san|sama|chan|kun|dono|senpai|saa+n|cha+n|cha~n|ku+n|pi|P|poyo|cchi|chi|poo|than|kins)|"
    r"Trai-(?:pi(?:ppi|ii)?|P|poyo(?:-check)?|chan|cchi|chi|ny|nee)|"
    r"Train-(?:pi|P|poyo|chan|y)|"
    r"Tray-(?:chan|nay|Tray)|"
    r"Tra-chan|"
    r"T-Rain(?:ster|-pi|ppi|yo|poyo|ee|i)?|"
    r"Trainy(?:-[A-Za-z]+)?|Trainie|Trainey(?:-[A-Za-z]+)?"
    r")\b"
)

ALLOWLIST_FILE_TOKENS: dict[str, set[str]] = {
    "localized_data/assets/story/data/50/1031/storytimeline_501031304.json": {
        "Trainer-kun",
        "Trainer-chan",
    },
    "localized_data/assets/story/data/04/1069/storytimeline_041069007.json": {
        "Trainynotes",
    },
}

# Role-noun anti-pattern: determiner/possessive + Tore- honorific
# ("my Tore-san", "her Tore-kun", etc. should be "my trainer", "her trainer").
ROLE_NOUN_RE = re.compile(
    r"\b(?:my|your|his|her|our|their|a|an|the|any|every|no|some|new|own|"
    r"fellow|veteran|rookie|chief|head|personal|exclusive|assigned|"
    r"licensed|certified|official|prospective|former|current|future)\s+"
    r"Tore-(?:san|sama|chan|kun|dono|senpai)\b",
    re.IGNORECASE,
)

# Sentinel text_data_dict.json rows (cat -> index -> required substring).
TEXT_DATA_SENTINELS: dict[tuple[str, str], str] = {
    ("92", "41065006"): "Tore-pi",
    ("92", "41091004"): "Tore-cchi",
    ("181", "501065514"): "Tore-pi",
    ("185", "1065"): "Tore-pi",
    ("232", "347"): "Tore-pi",
    ("232", "575"): "Tore-pi",
    ("232", "1124"): "Tore-cchi",
    ("232", "1127"): "Tore-cchi",
    ("232", "1150"): "Tore-chan",
    ("232", "1153"): "Tore-chan",
    ("232", "1155"): "Tore-chan",
    ("232", "1157"): "Tore-chan",
    ("163", "1080"): "Tore-chan",
    ("469", "1091"): "Tore-cchi",
    ("88", "30249"): "Tore-chan",
}

# Sentinel character_system_text_dict.json rows (chara_id -> voice_id -> required substring).
CST_SENTINELS: dict[tuple[str, str], str] = {
    ("1001", "2032"): "Tore-san",      # Special Week: トレーナーさん
    ("1004", "2032"): "Tore-kun",      # Maruzensky: トレーナー君
    ("1012", "93005"): "Teach",        # Hishi Amazon: トレ公
    ("1024", "90001"): "Tore-chan",    # Mayano Top Gun: トレーナーちゃん
    ("1030", "2032"): "Big Brother",   # Rice Shower: お兄さま
    ("1032", "2032"): "guinea pig",    # Agnes Tachyon: モルモット君
    ("1038", "2032"): "Big Bro",       # Curren Chan: お兄ちゃん
    ("1065", "10002"): "Tore-pi",      # Daitaku Helios: トレぴ
    ("1072", "20003"): "Tore-dono",    # Yaeno Muteki: トレーナー殿
    ("1074", "2032"): "Tore-sama",     # Mejiro Bright: トレーナー様
    ("1080", "90010"): "Tore-chan",    # Transcend: トレちゃん
    ("1091", "90010"): "Tore-cchi",    # Vivlos: トレっち
    ("1121", "1213"): "my liege",      # Durandal: 我が君
    ("9052", "70000"): "my lord",      # Azuma: 貴方様
}

# Canonical voice bible trainer_term expectations.
BIBLE_SENTINELS: dict[str, str] = {
    "1001": "Tore-san",
    "1004": "Tore-kun",
    "1012": "Teach",
    "1024": "Tore-chan",
    "1030": "Big Brother",
    "1038": "Big Bro",
    "1065": "Tore-pi",
    "1072": "Tore-dono",
    "1074": "Tore-sama",
    "1080": "Tore-chan",
    "1091": "Tore-cchi",
    "9052": "my lord",
}


def check_localized_data() -> list[str]:
    errors: list[str] = []
    if not LD.exists():
        return [f"Missing localized_data directory: {LD}"]

    for p in sorted(LD.rglob("*.json")):
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(REPO_ROOT).as_posix()

        allowed = ALLOWLIST_FILE_TOKENS.get(rel, set())
        bad = [m for m in FORBIDDEN_TOKEN_RE.findall(text) if m not in allowed]
        if bad:
            sample = ", ".join(sorted(set(bad))[:5])
            errors.append(f"{rel}: contains retired trainer token(s): {sample} ({len(bad)} hit(s))")

        rn = ROLE_NOUN_RE.findall(text)
        if rn:
            sample = ", ".join(sorted(set(rn))[:5])
            errors.append(f"{rel}: contains determiner + Tore- role noun: {sample} ({len(rn)} hit(s))")

    # Sentinel checks on text_data_dict.json
    td_path = LD / "text_data_dict.json"
    if td_path.exists():
        td = json.loads(td_path.read_text(encoding="utf-8"))
        for (cat, idx), expected in TEXT_DATA_SENTINELS.items():
            val = td.get(cat, {}).get(idx, "")
            if expected not in val:
                errors.append(
                    f"text_data_dict.json [{cat}/{idx}]: expected {expected!r} in {val!r}"
                )

    # Sentinel checks on character_system_text_dict.json
    cst_path = LD / "character_system_text_dict.json"
    if cst_path.exists():
        cst = json.loads(cst_path.read_text(encoding="utf-8"))
        for (cid, vid), expected in CST_SENTINELS.items():
            val = cst.get(cid, {}).get(vid, "")
            if expected not in val:
                errors.append(
                    f"character_system_text_dict.json [{cid}/{vid}]: expected {expected!r} in {val!r}"
                )

    return errors


def check_voice_bible() -> list[str]:
    errors: list[str] = []
    if not BIBLE_PATH.exists():
        return [f"Missing voice bible: {BIBLE_PATH}"]

    bible = json.loads(BIBLE_PATH.read_text(encoding="utf-8"))
    for cid, expected in BIBLE_SENTINELS.items():
        entry = bible.get(cid)
        if not entry:
            errors.append(f"uma_voice_bible.json: missing character {cid}")
            continue
        term = entry.get("trainer_term", "")
        if term != expected:
            errors.append(
                f"uma_voice_bible.json [{cid} {entry.get('en','')}]: trainer_term={term!r}, expected {expected!r}"
            )

    for cid, entry in bible.items():
        term = entry.get("trainer_term", "")
        if FORBIDDEN_TOKEN_RE.search(term):
            errors.append(
                f"uma_voice_bible.json [{cid} {entry.get('en','')}]: forbidden trainer_term={term!r}"
            )

    if CANONICAL_VOICE_PATH.exists():
        cv_text = CANONICAL_VOICE_PATH.read_text(encoding="utf-8")
        if '"default": "Tore-san"' not in cv_text:
            errors.append("canonical_voice.py: TRAINER_TERMS['default'] must be 'Tore-san'")

    return errors


def check_sync_scripts() -> list[str]:
    errors: list[str] = []
    if SYNC_UMATL_PATH.exists():
        st = SYNC_UMATL_PATH.read_text(encoding="utf-8")
        for pair in ('("Trainer-san", "Tore-san")', '("Trai-pi", "Tore-pi")'):
            if pair not in st:
                errors.append(f"sync_umatl.py: missing canonical rule {pair}")
    if SYNC_GLOBAL_PATH.exists():
        sg = SYNC_GLOBAL_PATH.read_text(encoding="utf-8")
        if "pinned_trainer_honorific" not in sg:
            errors.append("sync_global.py: missing pinned_trainer_honorific() guard")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_localized_data())
    errors.extend(check_voice_bible())
    errors.extend(check_sync_scripts())

    if errors:
        print(f"FAIL: {len(errors)} trainer-honorific guard violation(s):", file=sys.stderr)
        for e in errors[:50]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        return 1

    print(
        "OK: trainer-honorific guard passed "
        f"({len(TEXT_DATA_SENTINELS)} text_data sentinels, "
        f"{len(CST_SENTINELS)} cst sentinels, "
        f"{len(BIBLE_SENTINELS)} voice-bible sentinels, 0 retired tokens)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
