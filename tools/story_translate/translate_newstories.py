"""
translate_newstories.py - Translate new-story batch (game update 2026-09-10).
116 storytimeline files (new horse 1149, event 41149, career 82/83, misc).
Uses OmniRoute antigravity/gemini-3.8-flash-tiered (low effort) with fallback.
Pre-resolves speaker names from voice bible (1149 Phalaenopsis included).
"""
import json, os, sys, time, re, urllib.request, urllib.error, argparse, logging
from pathlib import Path

STORY_DIR = Path(r'C:\TMP\newstory_json')
WORK_DIR = Path(r'G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\tools\story_translate')
CHECKPOINT_PATH = WORK_DIR / 'newstories_checkpoint.json'
FILEMAP_PATH = WORK_DIR / 'newstories_file_map.json'
LOG_PATH = WORK_DIR / 'translate_newstories.log'
API_URL = "http://127.0.0.1:20128/v1/chat/completions"

import socket
socket.setdefaulttimeout(150)

PRIMARY_MODEL = "antigravity/gemini-3.8-flash-tiered"
FALLBACK_MODEL = "antigravity/gemini-3.8-flash-tiered"
EFFORT = "low"

BATCH_SIZE = 120

GLOSSARY = [
    ("\u5348\u5f0f\u99ff\u5927\u796d", "Goshiki Shuntaisai"),
    ("\u99ff\u5927\u796d", "Shuntaisai"),
    ("\u6f14\u76ee\u7a3d\u53e4", "Program Rehearsal"),
    ("\u6f14\u76ee", "Program"),
    ("\u543e\u59bb", "Azuma"),
]


RATE_LIMIT = 0.25
TIMEOUT = 120
MAX_TOKENS = 32000
BACKOFF_429 = [10, 20, 30]

WORK_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(LOG_PATH), level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s', filemode='a')
log = logging.getLogger('translate_newstories')

BIBLE_PATH = Path(__file__).resolve().parents[2] / "tools" / "voice_bible" / "uma_voice_bible.json"


def get_api_key():
    for ep in (r"C:\Users\Ota\.omniroute\.env",):
        if os.path.exists(ep):
            with open(ep, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    if 'API_KEY' in k.strip():
                        return v.strip().strip('"').strip("'")
    raise RuntimeError("No API key found in C:\\Users\\Ota\\.omniroute\\.env")


def load_voice_bible():
    """Load the character voice bible.

    A missing or empty bible is fatal by design: translating without it silently
    produces off-voice lines (wrong NPC names, nicknames and register), which is
    exactly the bug class the bible exists to prevent.
    """
    try:
        with open(BIBLE_PATH, 'r', encoding='utf-8') as f:
            bible = json.load(f)
    except Exception as e:
        raise SystemExit(f"voice bible not readable at {BIBLE_PATH}: {e}")
    if not bible:
        raise SystemExit(f"voice bible is empty: {BIBLE_PATH}")
    return bible


def is_japanese(text):
    if not text:
        return False
    return any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'
               or '\u4e00' <= c <= '\u9fff' for c in text)


def clean_newlines(s):
    if not isinstance(s, str):
        return s
    return s.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\r\n', '\n')


def extract_all_items(story_dir, voice_bible):
    jp_to_en = {}
    for cid, entry in voice_bible.items():
        if entry.get('jp') and entry.get('en'):
            jp_to_en[entry['jp']] = entry['en']
    jp_to_en.update({'吾妻': 'Azuma', 'モノローグ': 'Monologue', '？？？': '???', '？？？？': '???',
                     'トレーナー': 'Trainer', '記者': 'Reporter', '実況': 'Announcer',
                     '解説': 'Commentator', '観客': 'Spectator', 'ファン': 'Fan'})
    items, pre_resolved, file_map = [], {}, {}
    story_files = sorted(list(story_dir.rglob('storytimeline_*.json'))
                         + list(story_dir.rglob('hometimeline_*.json')))
    log.info(f"Found {len(story_files)} story files")
    for fpath in story_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            log.warning(f"read {fpath}: {e}")
            continue
        file_key = fpath.stem.replace('storytimeline_', '')
        file_map[file_key] = str(fpath.relative_to(story_dir)).replace('\\', '/')
        title = data.get('title')
        if title and isinstance(title, str) and title.strip() and is_japanese(title):
            items.append({'id': f'{file_key}__T', 'jp': title, 'kind': 'title'})
        for i, block in enumerate(data.get('text_block_list', [])):
            text = block.get('text', '')
            if text and text.strip() and is_japanese(text):
                items.append({'id': f'{file_key}__B{i}', 'jp': text})
            name = block.get('name')
            if name and isinstance(name, str) and name.strip():
                nid = f'{file_key}__N{i}'
                if name in jp_to_en:
                    pre_resolved[nid] = jp_to_en[name]
                elif is_japanese(name):
                    items.append({'id': nid, 'jp': name})
            for j, choice in enumerate(block.get('choice_data_list', [])):
                if choice and isinstance(choice, str) and choice.strip() and is_japanese(choice):
                    items.append({'id': f'{file_key}__C{i}_{j}', 'jp': choice})
            for j, color in enumerate(block.get('color_text_info_list', [])):
                ctext = color.get('Text') if isinstance(color, dict) else None
                if ctext and isinstance(ctext, str) and ctext.strip() and is_japanese(ctext):
                    items.append({'id': f'{file_key}__X{i}_{j}', 'jp': ctext, 'kind': 'name'})
    return items, pre_resolved, file_map


def build_system_prompt(voice_bible):
    lines = [
        "You are an expert Japanese-to-English game localization translator specializing in Umamusume: Pretty Derby (Cygames).",
        "Translate the provided Japanese batch array into natural, immersive, high-quality English for story dialogue, narration, and player choices.",
        "",
        "CRITICAL RULES:",
        '1. Output ONLY a valid JSON array of objects: [{"id": "<id>", "en": "<english_text>"}]. No markdown code fences, no extra text, no commentary.',
        "2. Preserve ALL formatting tokens, tags, and placeholders EXACTLY: {0}, {1}, {2}, <color=#RRGGBB>, </color>, <chrname>, <support>, \\n, \\t, ---.",
        "3. Do NOT omit any items. Return an entry for EVERY input item in exact matching order.",
        "4. Dialogue lines: write engaging, personality-rich English dialogue appropriate for each character.",
        "5. Character names: use official English names where known. E.g.:",
        "   オグリキャップ → Oguri Cap, ファレノプシス → Phalaenopsis, エピファネイア → Epiphaneia, シーザリオ → Cesario",
        "   ヴィルシーナ → Verxina, ジェンティルドンナ → Gentildonna, タイキシャトル → Taiki Shuttle",
        "   トメさん → Tome-san, シゲさん → Shige-san, チヨさん → Chiyo-san, ヨシさん → Yoshi-san",
        "6. NPC speaker names: translate to concise English (e.g. 陽気な生徒A → Cheerful Student A, ウマ娘A → Horsegirl A).",
        "7. Player choice options: translate with natural dialogue tone matching the context.",
        "8. Line breaks: preserve the exact newline structure from the original Japanese text. Do not invent extra newlines.",
        "9. Items with kind 'name' are character names or glossary terms. Return the official English name or term only.",
        "10. Items with kind 'title' are story titles. Keep them concise and consistent with the in-game UI.",
        "11. Speaker names (kind 'name' or bare names in block 'name' fields) must be plain English. Never return a Japanese name.",
        "12. In-dialogue nicknames for OTHER characters: drop Japanese honorifics (さん/ちゃん/先輩/君) and use the character's full official English name.",
        "    e.g. ハートさん → Daring Heart, エピ先輩 → Epiphaneia, アイ先輩/アイちゃん → Almond Eye, タイちゃん/タイホさん → Titleholder,",
        "    マリリンさん → Win Marilyn, タクトちゃん/タクトさん → Daring Tact, ブーケさん → Curren Bouquetd'or, ラヴちゃん → Loves Only You.",
        "13. TRAINER ADDRESS (MANDATORY): Keep each character's unique Japanese trainer address on the literal romaji stem 'Tore-':",
        "    トレーナーさん → Tore-san | トレーナーさま/様 → Tore-sama | トレーナーちゃん → Tore-chan",
        "    トレーナーくん/君 → Tore-kun | トレーナー殿 → Tore-dono | トレーナー先輩 → Tore-senpai",
        "    トレぴ → Tore-pi (Daitaku Helios; トレぴっぴ → Tore-pipi, トレぽよ → Tore-poyo)",
        "    トレちゃん → Tore-chan (Transcend; トレちゃーん → Tore-chaaan)",
        "    トレっち → Tore-cchi (Vivlos) | トレ公 → Teach (Hishi Amazon)",
        "    お兄さま → Big Brother (Rice Shower) | お兄ちゃん → Big Bro (Curren Chan)",
        "    モルモット → guinea pig (Agnes Tachyon) | カイチョー → Prez (Tokai Teio)",
        "    我が君 → my liege, 我が王 → my King, 主/主君 → my lord (Durandal)",
        "    Plain トレーナー (no honorific) and role-noun uses ('my trainer', 'her trainer', 'a trainer') stay 'Trainer'/'trainer'.",
        "    NEVER output 'Trainer-san/-chan/-kun/-sama/-dono', 'T-Rain', 'Trai-pi', 'Trai-chan', 'Trainy', or 'Trainie'.",
        "14. Daring Tact speaks calm, polite desu/masu register; 私 = 'I'; she calls the trainer 'Tore-san' (トレーナーさん); ふふ → 'Hehe.'",
    ]
    lines += ["", "SERIES GLOSSARY (use exactly):"]
    for jp, en in GLOSSARY:
        lines.append(f"- {jp} -> {en}")
    if voice_bible:
        lines += ["", "CHARACTER VOICE BIBLE (Archetypes, Tone & Trainer Address):"]
        for cid, entry in sorted(voice_bible.items(),
                                 key=lambda x: int(x[0]) if x[0].isdigit() else 9999):
            en, arch, tags = entry.get('en', ''), entry.get('archetype', ''), entry.get('speech_tags', '')
            tterm = entry.get('trainer_term', '')
            if en and arch:
                t_part = f" | Calls trainer: {tterm}" if tterm else ""
                lines.append(f"- {en}: {arch}. Tone: {tags}{t_part}")
    return "\n".join(lines)


def parse_translations(text):
    res = {}
    if not text:
        return res
    tc = re.sub(r'^```json\s*', '', text.strip(), flags=re.MULTILINE)
    tc = re.sub(r'^```\s*', '', tc, flags=re.MULTILINE).strip()
    try:
        data = json.loads(tc)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "id" in item and "en" in item:
                    res[item["id"]] = clean_newlines(item["en"])
            if res:
                return res
    except Exception:
        pass
    m = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item and "en" in item:
                        res[item["id"]] = clean_newlines(item["en"])
                if res:
                    return res
        except Exception:
            pass
    pair = re.compile(r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"en"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}')
    for match in pair.finditer(text):
        try:
            en_val = json.loads(f'"{match.group(2)}"')
        except Exception:
            en_val = match.group(2)
        res[match.group(1)] = clean_newlines(en_val)
    return res


def call_api(model, system_prompt, batch, api_key):
    payload = {"model": model, "effort": EFFORT,
               "messages": [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": json.dumps(batch, ensure_ascii=False)}],
               "temperature": 0.2, "max_tokens": MAX_TOKENS}
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode('utf-8'),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8'))['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')[:200]
        except Exception:
            body = ""
        return None, f"HTTP {e.code} {body}"
    except Exception as e:
        return None, f"REQ {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--story-dir", type=str, default=str(STORY_DIR))
    ap.add_argument("--work-dir", type=str, default=str(WORK_DIR))
    ap.add_argument("--checkpoint", type=str, default="")
    args = ap.parse_args()
    api_key = get_api_key()
    bible = load_voice_bible()
    story_dir = Path(args.story_dir)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = Path(args.checkpoint) if args.checkpoint else (work_dir / 'newstories_checkpoint.json')
    filemap_path = work_dir / 'newstories_file_map.json'

    items, pre_resolved, file_map = extract_all_items(story_dir, bible)
    with open(filemap_path, 'w', encoding='utf-8') as f:
        json.dump({"files": file_map, "pre_resolved": pre_resolved}, f, ensure_ascii=False)
    checkpoint = {}
    if checkpoint_path.exists():
        try:
            checkpoint = json.load(open(checkpoint_path, encoding='utf-8'))
        except Exception as e:
            log.warning(f"checkpoint load: {e}")
    checkpoint.update(pre_resolved)
    pending = [e for e in items if e["id"] not in checkpoint]
    if args.limit > 0:
        pending = pending[:args.limit]
    print(f"items={len(items)} pre_resolved={len(pre_resolved)} pending={len(pending)}", flush=True)
    if not pending:
        print("nothing pending")
        return
    prompt = build_system_prompt(bible)
    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    failed = 0
    t0 = time.time()
    for idx, batch in enumerate(batches, 1):
        parsed, success = {}, False
        models = [PRIMARY_MODEL] * 3 + [FALLBACK_MODEL]
        for attempt, model in enumerate(models):
            raw, err = call_api(model, prompt, batch, api_key)
            if err:
                print(f"  [B{idx}] {model} err {err}, retry...", flush=True)
                time.sleep(BACKOFF_429[min(attempt, 2)] if err.startswith("HTTP 429") else 2)
                continue
            parsed = parse_translations(raw)
            if len(parsed) >= len(batch) * 0.8:
                success = True
                break
            print(f"  [B{idx}] partial {len(parsed)}/{len(batch)}, retry...", flush=True)
        if success and parsed:
            checkpoint.update({k: v for k, v in parsed.items()})
            json.dump(checkpoint, open(checkpoint_path, 'w', encoding='utf-8'), ensure_ascii=False)
            el = time.time() - t0
            print(f"[B{idx}/{len(batches)}] ok +{len(parsed)} total={len(checkpoint)} elapsed={el:.0f}s", flush=True)
        else:
            failed += 1
            print(f"[B{idx}/{len(batches)}] FAILED", flush=True)
        time.sleep(RATE_LIMIT)
    print(f"done failed={failed} checkpoint={len(checkpoint)}")


if __name__ == "__main__":
    main()
