"""Mine per-character voice evidence from JP master + EN (Global first, then us).

Writes tools/voice_bible/voice_evidence.json:
  id -> {
    lines_jp, lines_global, lines_ours,
    self_name: [[token, n], ...],          # third-person self reference
    pronoun: [[jp, n], ...],               # first-person pronouns
    trainer: {jp_term: {en_form: n}}       # how we/Global render trainer address
    markers: {tag: [n, ratio_vs_cast]}
    tags: [...]
    samples: [{jp, en, src}]               # up to 3 example pairs (Global preferred)
  }
"""
import sqlite3, json, re, pathlib, collections, statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
JP = ROOT.parent / "UmamusumePrettyDerby_Jpn_Data/Persistent/master/master.mdb"
GL = ROOT.parent.parent / "UmamusumePrettyDerby/UmamusumePrettyDerby_Data/Persistent/master/master.mdb"
CST_EN = ROOT / "localized_data/character_system_text_dict.json"
OUT = ROOT / "tools/voice_bible/voice_evidence.json"

jp = sqlite3.connect(JP); jp.text_factory = bytes
gl = sqlite3.connect(GL); gl.text_factory = bytes


def dec(b):
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


names = {i: dec(t) for i, t in jp.execute("select `index`, text from text_data where category=6")}
# 182 = katakana reading (the in-game furigana for NPCs / alias forms)
reads = {i: dec(t) for i, t in jp.execute("select `index`, text from text_data where category=182")}
gl_names = {i: dec(t) for i, t in gl.execute("select `index`, text from text_data where category=6")}
cst_en = json.load(open(CST_EN, encoding="utf-8"))

jp_lines = collections.defaultdict(list)
for cid, vid, txt in jp.execute("select character_id, voice_id, text from character_system_text"):
    jp_lines[cid].append((vid, dec(txt).replace("\r\n", "\n")))
gl_lines = {(c, v): dec(t).replace("\r\n", "\n") for c, v, t in
            gl.execute("select character_id, voice_id, text from character_system_text")}

L = {  # marker lexicons
    "kansai": ["ほんま", "やけど", "あかん", "せや", "やで", "おおきに", "なんや", "まう", "しとる", "やろな", "やないか", "えらい"],
    "hokkaido": ["なまら", "したっけ", "だべさ", "めんこい", "ちょす", "はんかくさい", "なして"],
    "tohoku": ["なはん", "がんす", "めんごい", "んだべ", "んだがら", "おらだ"],
    "desuwa": ["ですわ", "ますわ", "ざます", "ますのよ", "ですのよ"],
    "archaic": ["我が君", "我が王", "主君", "たまえ", "であるぞ", "なのだぞ", "おるのじゃ", "〜ぬ", "ぬ。"],
    "rough": ["てめえ", "おめえ", "やがる", "だぜ", "ぶっ", "くそ", "ざけん", "すんぞ", "しねえ"],
    "gyaru": ["マジ", "ぴえん", "エモい", "それな", "っしょ", "じゃん", "やばい", "すこ", "きゅん"],
    "keigo": ["です", "ます", "ございます", "いらっしゃ", "いたします"],
}
PRONOUNS = ["私", "わたし", "ワタシ", "あたし", "アタシ", "ウチ", "俺", "オレ", "ボク", "ぼく", "自分", "わし", "わらわ", "余", "吾輩"]
SELF_NICK = {"1003": "テイオー", "1014": "エル", "1024": "マヤ", "1030": "ライス",
             "1038": "カレン", "1046": "ファル子", "1052": "ウララ", "1066": "ターボ"}
TRAINER = ["トレーナーさん", "トレーナー", "トレぴ", "トレぴっぴ", "トレちゃん", "トレーナーちゃん",
           "トレーナー君", "トレーナー殿", "トレーナーどの", "先生", "トレぴー", "トレちん", "トレぽよ"]

raw = {}
for cid, rows in jp_lines.items():
    if cid > 10000:  # 2xxx/9xxx NPCs kept; this filters card variants if any
        pass
    texts = [t for _, t in rows]
    joined = "\n".join(texts)
    name = names.get(cid, "")
    aliases = {a for a in (name, reads.get(cid, "")) if a and len(a) >= 2}
    if str(cid) in SELF_NICK:
        aliases.add(SELF_NICK[str(cid)])
    self_name = collections.Counter()
    for t in texts:
        for a in aliases:
            self_name[a] += t.count(a)
    pron = collections.Counter({p: joined.count(p) for p in PRONOUNS if joined.count(p)})
    markers = {}
    for tag, words in L.items():
        n = sum(joined.count(w) for w in words)
        markers[tag] = n
    katakana = len(re.findall(r"[A-Za-z]{2,}", joined))
    trainer = collections.defaultdict(collections.Counter)
    samples = []
    for vid, t in rows:
        g = gl_lines.get((cid, vid))
        ours = (cst_en.get(str(cid)) or {}).get(str(vid)) or ""
        en = g or ours
        for term in TRAINER:
            if term in t:
                trainer[term][en and "GLOBAL" or "OURS"] += 1
                # record the actual EN substring around trainer mentions later
        if g and len(samples) < 40:
            samples.append({"vid": vid, "jp": t, "en": g, "src": "global"})
        elif ours and len(samples) < 40:
            samples.append({"vid": vid, "jp": t, "en": ours, "src": "ours"})
    # how the trainer term is actually rendered: keep the EN of lines containing it
    trainer_lines = []
    for vid, t in rows:
        hit = [x for x in TRAINER if x in t]
        if not hit:
            continue
        g = gl_lines.get((cid, vid))
        ours = (cst_en.get(str(cid)) or {}).get(str(vid)) or ""
        en = g or ours
        if en:
            trainer_lines.append({"jp_term": hit[0], "jp": t, "en": en, "src": "global" if g else "ours"})
    raw[cid] = {
        "jp": name,
        "reading": reads.get(cid, ""),
        "global_en": gl_names.get(cid, ""),
        "lines_jp": len(texts),
        "lines_global": sum(1 for vid, _ in rows if (cid, vid) in gl_lines),
        "lines_ours": sum(1 for vid, _ in rows if ((cst_en.get(str(cid)) or {}).get(str(vid)))),
        "self_name": self_name.most_common(3),
        "pronoun": pron.most_common(4),
        "markers": markers,
        "katakana_tokens": katakana,
        "trainer_lines": trainer_lines[:12],
        "samples": samples[:4],
    }

# cast averages for markers, for ratio scoring
tot = collections.Counter()
for v in raw.values():
    for tag, n in v["markers"].items():
        tot[tag] += n
cast = {t: tot[t] / max(1, len(raw)) for t in tot}

TAG_RULES = [
    ("kansai", 8, "kansai-dialect"),
    ("hokkaido", 5, "hokkaido-dialect"),
    ("tohoku", 4, "tohoku-dialect"),
    ("desuwa", 12, "ojou-desuwa"),
    ("archaic", 8, "archaic-register"),
    ("rough", 12, "rough-speech"),
    ("gyaru", 10, "gyaru-slang"),
]

for cid, v in raw.items():
    tags = []
    for key, floor, tag in TAG_RULES:
        n = v["markers"][key]
        if n >= floor and n >= 4 * max(1.0, cast[key]):
            tags.append(tag)
    if v["katakana_tokens"] >= 30:
        tags.append("katakana-english")
    if v["self_name"] and v["self_name"][0][1] >= 8:
        tags.append("third-person-self")
    v["tags"] = tags

json.dump({str(k): v for k, v in raw.items()}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {len(raw)} entries -> {OUT}")
print("tag counts:", collections.Counter(t for v in raw.values() for t in v["tags"]).most_common())
print("cast marker averages:", {k: round(v, 1) for k, v in cast.items()})
