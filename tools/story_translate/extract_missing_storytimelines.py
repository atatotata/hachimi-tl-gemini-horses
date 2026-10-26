"""
extract_missing_storytimelines.py
Extract new JP storytimeline assets that are referenced by single_mode_story_data
but are not yet present in the repo. Reads the local encrypted meta and dat files.

Output: <out>/story_json/<asset path>/storytimeline_<id>.json
        <out>/file_map.json
"""
import json
import os
import sys
from pathlib import Path

import apsw
import UnityPy

GAME = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn")
DATA = GAME / "UmamusumePrettyDerby_Jpn_Data"
DAT_DIR = DATA / "Persistent" / "dat"
META_PATH = DATA / "Persistent" / "meta"
MASTER_PATH = DATA / "Persistent" / "master" / "master.mdb"
REPO_STORY = GAME / "gemini_horses" / "localized_data" / "assets" / "story" / "data"
OUT_DIR = Path(r"E:\AI_Offload\TMP\opencode\new_scenario_fetch")
STORY_JSON_DIR = OUT_DIR / "story_json"

sys.path.insert(0, str(GAME / "gemini_horses" / "tools" / "umamusu-utils" / "scripts"))
from utils import _derive_decryption_key, _derive_asset_key, DB_KEY, DB_BASE_KEY, dict_factory


def existing_ids():
    ids = set()
    for p in REPO_STORY.rglob("storytimeline_*.json"):
        try:
            ids.add(int(p.stem.replace("storytimeline_", "")))
        except ValueError:
            pass
    return ids


def missing_ids():
    import sqlite3
    conn = sqlite3.connect(str(MASTER_PATH))
    ids = sorted({r[0] for r in conn.execute("SELECT story_id FROM single_mode_story_data")})
    conn.close()
    have = existing_ids()
    return [sid for sid in ids if sid not in have]


def resolve_meta(ids):
    conn = apsw.Connection(str(META_PATH))
    conn.row_trace = dict_factory
    conn.pragma("cipher", "chacha20")
    conn.pragma("hexkey", _derive_decryption_key(DB_KEY, DB_BASE_KEY).hex())
    cur = conn.cursor()
    out = {}
    for sid in ids:
        rows = cur.execute(
            "SELECT n, h, e, m FROM a WHERE n LIKE ?", (f"%/storytimeline_{sid}",)
        ).fetchall()
        if rows:
            out[sid] = rows[0]
    return out


def decrypt_bundle(h, e):
    path = DAT_DIR / h[:2] / h
    if not path.exists():
        raise FileNotFoundError(path)
    data = bytearray(path.read_bytes())
    key = _derive_asset_key(e)
    if key and len(data) > 256:
        klen = len(key)
        for i in range(256, len(data)):
            data[i] ^= key[i % klen]
    return bytes(data)


def extract_bundle(data, basename):
    env = UnityPy.load(data)
    timeline = None
    clips = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
            if not isinstance(tree, dict):
                continue
            if "BlockList" in tree:
                if tree.get("m_Name") == basename:
                    timeline = tree
                elif timeline is None:
                    timeline = tree
            elif "Text" in tree and "ChoiceDataList" in tree:
                clips[obj.path_id] = tree
        except Exception:
            pass
    if timeline is None:
        raise ValueError(f"No BlockList in {basename}")

    blocks = []
    for block_index, block in enumerate(timeline.get("BlockList", [])):
        item = {}
        track = block.get("TextTrack") or {}
        for clip_ref in track.get("ClipList", []):
            clip = clips.get(clip_ref.get("m_PathID"))
            if not clip:
                continue
            name = clip.get("Name") or ""
            text = clip.get("Text") or ""
            choices = [
                c.get("Text", "")
                for c in clip.get("ChoiceDataList", [])
                if c.get("Text")
            ]
            colors = clip.get("ColorTextInfoList") or []
            if name:
                item["name"] = name
            if text:
                item["text"] = text
            if choices:
                item["choice_data_list"] = choices
            if colors:
                item["color_text_info_list"] = colors
            break

        # The engine's block 0 is an empty lead-in. Repo files start at block 1.
        if block_index == 0 and not item:
            continue
        blocks.append(item)

    title = timeline.get("Title") or ""
    out = {"no_wrap": True, "text_block_list": blocks}
    if title:
        out["title"] = title
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STORY_JSON_DIR.mkdir(parents=True, exist_ok=True)

    ids = missing_ids()
    print(f"Missing storytimeline IDs: {len(ids)}")
    resolved = resolve_meta(ids)
    print(f"Resolved in meta: {len(resolved)} / {len(ids)}")

    file_map = {}
    total_blocks = 0
    total_colors = 0
    failures = []

    for n, (sid, info) in enumerate(sorted(resolved.items()), 1):
        asset = info["n"]
        parts = asset.split("/")
        rel = Path(*parts[2:]) if len(parts) > 2 else Path(f"storytimeline_{sid}")
        out_file = STORY_JSON_DIR / rel.parent / f"{rel.name}.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = decrypt_bundle(info["h"], info["e"])
            story = extract_bundle(data, rel.name)
            out_file.write_text(
                json.dumps(story, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            file_map[str(sid)] = str(out_file.relative_to(STORY_JSON_DIR)).replace("\\", "/")
            total_blocks += len(story["text_block_list"])
            total_colors += sum(
                len(b.get("color_text_info_list", [])) for b in story["text_block_list"]
            )
            print(f"[{n}/{len(resolved)}] {sid} -> {len(story['text_block_list'])} blocks")
        except Exception as exc:
            failures.append((sid, str(exc)))
            print(f"[{n}/{len(resolved)}] FAILED {sid}: {exc}")

    (OUT_DIR / "file_map.json").write_text(
        json.dumps(file_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Extracted: {len(file_map)} files, {total_blocks} blocks, {total_colors} color spans")
    if failures:
        print(f"Failures: {len(failures)}")
        for sid, err in failures:
            print(f"  {sid}: {err}")


if __name__ == "__main__":
    main()
