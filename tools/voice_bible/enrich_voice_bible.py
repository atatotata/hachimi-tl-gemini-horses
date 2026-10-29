"""Step 2 (v2): voice-bible enrichment grounded in real dialogue evidence.

For every bible entry, feed the model deterministic evidence mined by
mine_voice.py (pronouns, third-person self-reference, dialect markers, trainer
address renderings with Global provenance, and JP/EN sample pairs) and ask for
an archetype, speech tags, the EN trainer address, and one verbal-habit note.

Resume-safe: entries with voice_v == 2 and an archetype are skipped unless
--force is passed. No API key is stored in this file.
"""
import json, os, sys, time, urllib.request, pathlib

ROOT = pathlib.Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses")
BIBLE = ROOT / "tools/voice_bible/uma_voice_bible.json"
EVID = ROOT / "tools/voice_bible/voice_evidence.json"
sys.path.insert(0, str(ROOT / "tools/voice_bible"))
from canonical_voice import VOICE_NOTES, TRAINER_TERMS

URL = "http://127.0.0.1:20128/v1/chat/completions"
MODEL = "antigravity/gemini-3.8-flash-tiered"
BATCH = 16
ENV_CANDIDATES = [
    pathlib.Path(os.path.expanduser("~/.omniroute/.env")),
    ROOT / ".omniroute/.env",
]


def get_key():
    for env in ENV_CANDIDATES:
        if not env.exists():
            continue
        for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if "KEY" in k.upper() and v.strip():
                return v.strip().strip('"').strip("'")
    raise SystemExit(f"no API key found in {[str(p) for p in ENV_CANDIDATES]}")


KEY = get_key()

SYS = (
    "You are maintaining a character voice bible for the English fan translation of "
    "Umamusume: Pretty Derby. Each entry ships a compact, evidence-based voice spec "
    "that translators and MT prompts follow, so it must reflect how the character "
    "ACTUALLY talks in the supplied dialogue samples -- not guesses from her name.\n"
    "Rules:\n"
    "- archetype: 5-12 words, concrete delivery direction (e.g. 'kansai auntie who "
    "teases, then mothers you').\n"
    "- speech_tags: 3-6 short kebab-case tags. Reuse every 'evidence tags' value "
    "verbatim; add tone/register tags only when the samples support them.\n"
    "- trainer_term: how she addresses the trainer in English. If a Global "
    "rendering is listed, use it exactly. If 'canonical' is listed, use that. "
    "Otherwise use 'Trainer', or a specific term only if the samples show one. "
    "Empty string if she never addresses the trainer.\n"
    "- notes: ONE sentence, max 20 words, naming a specific verbal habit visible "
    "in the samples (catchphrase, sentence ending, honorific, code-switch).\n"
    "Never invent dialect, catchphrases or honorifics that the evidence does not show. "
    "Output ONLY a JSON array of objects with keys "
    '"id","archetype","speech_tags","trainer_term","notes". No prose, no fences.'
)


def compact(cid, entry, ev):
    parts = [f'{cid} | {entry.get("en") or ev.get("global_en") or entry.get("jp")}', ]
    trait = (entry.get("trait_en") or "").replace("\n", " ")[:160]
    if trait:
        parts.append(f'trait: {trait}')
    if ev:
        parts.append(f'JP lines: {ev["lines_jp"]} (Global {ev["lines_global"]})')
        if ev.get("pronoun"):
            parts.append("pronouns: " + ", ".join(f"{p}{n}" for p, n in ev["pronoun"]))
        if ev.get("self_name"):
            terms = [f"{t}{n}" for t, n in ev["self_name"] if n]
            if terms:
                parts.append("self-reference: " + ", ".join(terms))
        if ev.get("tags"):
            parts.append("evidence tags: " + ", ".join(ev["tags"]))
        seen = set()
        tr = []
        for row in ev.get("trainer_lines") or []:
            term = row["jp_term"]
            if term in seen:
                continue
            seen.add(term)
            en = row["en"]
            # pull the phrase that follows the trainer wording, if recognisable
            tr.append(f'{term} => {en[:70]!r} ({row["src"]})')
        for term in seen:
            policy = TRAINER_TERMS.get(cid, {}).get("term") or TRAINER_TERMS["default"]
        if tr:
            parts.append("trainer renderings: " + "; ".join(tr[:2]))
        if cid in TRAINER_TERMS:
            parts.append("canonical trainer term: " + (TRAINER_TERMS[cid].get("term") or "Trainer"))
        for s in (ev.get("samples") or [])[:2]:
            parts.append(f'JP: {s["jp"][:90]!r} | EN({s["src"]}): {s["en"][:110]!r}')
    if VOICE_NOTES.get(cid):
        parts.append("known: " + VOICE_NOTES[cid])
    return " || ".join(parts)


def call(items):
    body = json.dumps({
        "model": MODEL, "effort": "low", "temperature": 0.2,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": "Entries:\n" + "\n".join(items)}],
        "max_tokens": 6000,
    }).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(URL, data=body, headers={
                "Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
            with urllib.request.urlopen(req, timeout=240) as r:
                out = json.load(r)["choices"][0]["message"]["content"].strip()
            if out.startswith("```"):
                out = out.strip("`").strip()
                if out.startswith("json"):
                    out = out[4:].strip()
            start = out.find("[")
            return json.loads(out[start:])
        except Exception as e:
            last = e
            print(f"  attempt {attempt+1}: {e!r}")
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"batch failed: {last!r}")


def main():
    force = "--force" in sys.argv
    limit = None
    for a in sys.argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
    bible = json.load(open(BIBLE, encoding="utf-8"))
    evid = json.load(open(EVID, encoding="utf-8"))
    todo = [k for k, v in bible.items()
            if force or not (v.get("voice_v") == 2 and v.get("archetype"))]
    if limit:
        todo = todo[:limit]
    print(f"{len(todo)} entries to enrich ({len(bible)} total)")
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        items = [compact(k, bible[k], evid.get(k)) for k in chunk]
        print(f"batch {i // BATCH + 1}/{(len(todo) + BATCH - 1) // BATCH}")
        rows = call(items)
        by_id = {str(r.get("id")): r for r in rows if isinstance(r, dict)}
        missing = [k for k in chunk if k not in by_id]
        if missing:
            print("  missing ids:", missing)
        for k, row in by_id.items():
            if k not in bible:
                continue
            e = bible[k]
            if row.get("archetype"):
                e["archetype"] = str(row["archetype"]).strip()
            tags = row.get("speech_tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            if tags:
                e["speech_tags"] = [str(t).strip() for t in tags][:6]
            e["trainer_term"] = str(row.get("trainer_term") or "").strip()
            e["notes"] = str(row.get("notes") or "").strip()
            e["voice_v"] = 2
        json.dump(bible, open(BIBLE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(0.4)
    done = sum(1 for v in bible.values() if v.get("voice_v") == 2)
    print(f"done: {done}/{len(bible)}")


if __name__ == "__main__":
    main()
