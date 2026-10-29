"""Rebuild uma_voice_bible.json from master.mdb + live text_data_dict (merge mode).

Base fields are re-derived every run:
  en        Global cat6 name when it exists, else our dict cat6 (canonicalised)
  jp        JP cat6 name
  reading   JP cat182 furigana (NPC ids only)
  trait_jp  JP cat144 trait (real newlines, no literal \\n)
  trait_en  our dict cat144 trait (Global text where we have it)
Enrichment fields are PRESERVED across rebuilds:
  archetype, speech_tags, trainer_term, notes, voice_v
speech_tags additionally absorbs the deterministic evidence tags mined by
mine_voice.py, so a plain rebuild no longer wipes voice work.
"""
import sqlite3, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/voice_bible"))
from canonical_voice import NAME_FIXES, TRAINER_TERMS, TAG_DENY

MDB_JP = ROOT.parent / "UmamusumePrettyDerby_Jpn_Data/Persistent/master/master.mdb"
MDB_GL = ROOT.parent.parent / "UmamusumePrettyDerby/UmamusumePrettyDerby_Data/Persistent/master/master.mdb"
LIVE_TD = ROOT / "localized_data/text_data_dict.json"
OUT = ROOT / "tools/voice_bible/uma_voice_bible.json"
EVID = ROOT / "tools/voice_bible/voice_evidence.json"

KEEP = ("archetype", "speech_tags", "trainer_term", "notes", "voice_v")


def read_master(path, cols):
    con = sqlite3.connect(path)
    con.text_factory = bytes
    out = {}
    for cat, idx, txt in con.execute(f"SELECT category, `index`, text FROM text_data WHERE category IN ({cols})"):
        out.setdefault(cat, {})[idx] = txt.decode("utf-8", "replace") if isinstance(txt, bytes) else str(txt)
    con.close()
    return out


def clean(s):
    if not s:
        return ""
    s = s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in s:
        s = s.replace("\n\n\n", "\n\n")
    return s.strip("\n")


def fix_name(n):
    for old, new in NAME_FIXES:
        n = n.replace(old, new)
    return n


jp = read_master(MDB_JP, "6,144,182")
gl = read_master(MDB_GL, "6")
live = json.load(open(LIVE_TD, encoding="utf-8"))

prev = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {}
evid = json.load(open(EVID, encoding="utf-8")) if EVID.exists() else {}

ids = sorted(set(jp.get(6, {})) | {int(k) for k in live.get("6", {}) if str(k).isdigit()})
bible = {}
for cid in ids:
    k = str(cid)
    old = prev.get(k, {})
    en = fix_name(gl.get(6, {}).get(cid) or live.get("6", {}).get(k, "") or old.get("en", ""))
    entry = {
        "en": en,
        "jp": jp.get(6, {}).get(cid, old.get("jp", "")),
        "reading": jp.get(182, {}).get(cid, old.get("reading", "")),
        "trait_jp": clean(jp.get(144, {}).get(cid, old.get("trait_jp", ""))),
        "trait_en": clean(live.get("144", {}).get(k, old.get("trait_en", ""))),
    }
    for f in KEEP:
        if f in old:
            entry[f] = old[f]
    entry.setdefault("archetype", "")
    entry.setdefault("speech_tags", [])
    entry.setdefault("trainer_term", TRAINER_TERMS.get(k, {}).get("term", ""))
    entry.setdefault("notes", "")
    ev_tags = (evid.get(k) or {}).get("tags") or []
    merged = list(dict.fromkeys([*ev_tags, *(entry.get("speech_tags") or [])]))
    merged = [t for t in merged if t not in TAG_DENY.get(k, set())]
    entry["speech_tags"] = merged
    bible[k] = entry

tmp = OUT.with_suffix(".json.tmp")
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(bible, fh, ensure_ascii=False, indent=1)
tmp.replace(OUT)
print(f"wrote {len(bible)} entries -> {OUT}")
print("with archetype:", sum(1 for v in bible.values() if v["archetype"]))
print("with tags:", sum(1 for v in bible.values() if v["speech_tags"]))
print("with trait_en:", sum(1 for v in bible.values() if v["trait_en"]))
print("new ids:", sorted(set(bible) - set(prev)))
print("dropped ids:", sorted(set(prev) - set(bible)))
