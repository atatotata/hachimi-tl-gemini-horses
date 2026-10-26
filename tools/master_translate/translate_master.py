import json
import time
import os
import sys
import re
import urllib.request
import urllib.error
import argparse

DUMP_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\tools\master_translate\master_untranslated.json"
CHECKPOINT_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\tools\master_translate\master_translated_checkpoint.json"
ENV_PATH = r"C:\Users\Ota\.omniroute\.env"
API_URL = "http://127.0.0.1:20128/v1/chat/completions"

PRIMARY_MODEL = "antigravity/gemini-3.8-flash-tiered"
FALLBACK_MODEL = "antigravity/gemini-3.8-flash-tiered"
EFFORT = "low"

def get_api_key():
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "VISION_BRIDGE_API_KEY" in line:
                    return line.strip().split("=", 1)[1].strip()
                elif "API_KEY" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        return parts[1].strip()
    raise RuntimeError("No API key found in C:\\Users\\Ota\\.omniroute\\.env")

def build_system_prompt(batch_items):
    # Detect active speakers
    speakers = {}
    has_ui = False
    has_skill = False
    has_story = False
    has_lore = False
    has_lyrics = False
    has_names = False
    name_hints = []

    for item in batch_items:
        if "speaker_name" in item and "speaker_archetype" in item and item["speaker_archetype"]:
            spk = item["speaker_name"]
            if spk not in speakers:
                speakers[spk] = item["speaker_archetype"]
        ctx = item.get("context", "")
        if ctx in ["UI_TEXT", "SHORT_LABEL", "RACE_NAME", "EVENT_NAME"]:
            has_ui = True
        elif ctx in ["SKILL_NAME", "SKILL_DESC", "MISSION"]:
            has_skill = True
        elif ctx in ["STORY_TITLE", "STORY_NARRATION", "NAME_TITLE"]:
            has_story = True
        elif ctx in ["LORE", "RITUAL"]:
            has_lore = True
        elif ctx == "LYRICS":
            has_lyrics = True
        elif ctx == "NAME":
            has_names = True
        hint = item.get("name_hint")
        if hint and hint not in name_hints:
            name_hints.append(hint)

    lines = [
        "You are an expert Japanese-to-English game localization translator specializing in Umamusume: Pretty Derby (Cygames).",
        "Translate the provided Japanese batch array into natural, high-quality English.",
        "",
        "CRITICAL RULES:",
        "1. Output ONLY a valid JSON array of objects: [{\"id\": \"<id>\", \"en\": \"<english_text>\"}]. No markdown code fences, no extra text.",
        "2. Preserve all formatting tokens, tags, and placeholders EXACTLY: {0}, {1}, <color=#...>, </color>, <chrname>, <support>, <race_name>, <character_name>, <bashin>, \\n, \\t.",
        "3. Do not omit any items. Return an entry for every input item in exact matching order."
    ]

    if has_ui:
        lines.append("\nUI & SHORT LABELS GUIDELINES:")
        lines.append("- For UI buttons, race names, and short labels: Keep translations concise and natural for mobile RPG UI. Avoid overly verbose phrasing to prevent UI button overflow. Use standard gaming/racing terminology.")

    if has_skill:
        lines.append("\nSKILLS & MISSIONS GUIDELINES:")
        lines.append("- For skills and missions: Use standard RPG clarity (e.g., 'Slightly increases speed in final stretch'). Preserve parameter placeholders like {0} and hardcoded line breaks.")

    if has_story:
        lines.append("\nSTORY & NARRATION GUIDELINES:")
        lines.append("- Use natural literary English. Keep the speaker's voice and the original line breaks. Do not add commentary or extra scenes.")

    if has_lore:
        lines.append("\nLORE & RITUAL GUIDELINES:")
        lines.append("- Keep a mythic, ceremonial tone. Preserve line breaks and do not explain the text or add notes.")

    if has_lyrics:
        lines.append("\nLYRICS GUIDELINES:")
        lines.append("- Translate as natural, singable English. Keep line breaks and preserve tags or placeholders.")

    if has_names:
        lines.append("\nNAME GUIDELINES:")
        lines.append("- Return the canonical English name only. Never translate a character name literally.")

    if name_hints:
        lines.append("\nCANONICAL NAMES:")
        for hint in name_hints:
            lines.append(f"- {hint}")

    if speakers:
        lines.append("\nACTIVE CHARACTER VOICES & PERSONAS:")
        for spk, arch in speakers.items():
            lines.append(f"- {spk}: {arch}")
        lines.append("- When translating lines for these characters, reflect their exact speech habits, personality, and tone faithfully.")

    return "\n".join(lines)

def parse_translations(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Attempt 1: Standard JSON parse
    try:
        data = json.loads(text)
        if isinstance(data, list):
            res = {}
            for item in data:
                if isinstance(item, dict) and "id" in item and "en" in item:
                    res[item["id"]] = item["en"]
            if res:
                return res
    except Exception:
        pass

    # Attempt 2: Regex JSON array extraction
    m = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                res = {item["id"]: item["en"] for item in data if isinstance(item, dict) and "id" in item and "en" in item}
                if res:
                    return res
        except Exception:
            pass

    # Attempt 3: Individual object regex extraction
    res = {}
    pattern = re.compile(r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"en"\s*:\s*"(.*?)(?<!\\)"\s*\}', re.DOTALL)
    for match in pattern.finditer(text):
        item_id = match.group(1)
        item_en = match.group(2).replace('\\"', '"').replace('\\n', '\n')
        res[item_id] = item_en

    return res

def call_api(api_key, model, system_prompt, user_payload, timeout=180):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
    ]
    data = {
        "model": model,
        "effort": EFFORT,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 32000
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]

def main():
    parser = argparse.ArgumentParser(description="Translate master.mdb untranslated strings")
    parser.add_argument("--batch-size", type=int, default=120, help="Batch size (default: 120)")
    parser.add_argument("--limit", type=int, default=0, help="Limit total items to translate for testing")
    parser.add_argument("--retry-failed", action="store_true", help="Only retranslate failed items")
    args = parser.parse_args()

    api_key = get_api_key()
    print(f"Loaded API key from env: {api_key[:8]}...{api_key[-4:]}")

    if not os.path.exists(DUMP_PATH):
        print(f"Error: Dump file {DUMP_PATH} not found. Run dump_untranslated_master.py first.")
        return

    with open(DUMP_PATH, "r", encoding="utf-8") as f:
        dump_data = json.load(f)

    all_entries = dump_data["entries"]
    print(f"Total entries in dump: {len(all_entries)}")

    # Load checkpoint
    checkpoint = {}
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            print(f"Loaded existing checkpoint: {len(checkpoint)} entries already translated")
        except Exception as e:
            print(f"Warning loading checkpoint: {e}")

    # Filter pending entries
    pending = [e for e in all_entries if e["id"] not in checkpoint]
    if args.limit > 0:
        pending = pending[:args.limit]

    print(f"Entries to translate: {len(pending)}")
    if not pending:
        print("All entries already translated in checkpoint!")
        return

    # Chunk into batches
    batch_size = args.batch_size
    batches = [pending[i:i + batch_size] for i in range(0, len(pending), batch_size)]
    print(f"Total batches to process: {len(batches)} (Batch size: {batch_size})")

    total_translated = len(checkpoint)
    start_time = time.time()
    failed_batches = 0

    for idx, batch in enumerate(batches, 1):
        batch_start = time.time()
        system_prompt = build_system_prompt(batch)
        user_payload = [{"id": e["id"], "jp": e["jp"]} for e in batch]

        success = False
        parsed = {}
        backoff = [5, 15, 30, 60, 120]

        for attempt in range(4):
            model = PRIMARY_MODEL if attempt < 3 else FALLBACK_MODEL
            try:
                print(f"[Batch {idx}/{len(batches)}] Attempt {attempt+1}: Sending {len(batch)} items to {model}...")
                raw_resp = call_api(api_key, model, system_prompt, user_payload)
                parsed = parse_translations(raw_resp)
                if len(parsed) >= len(batch) * 0.8:  # Accept if at least 80% parsed
                    success = True
                    break
                else:
                    print(f"  [Batch {idx}] Parse partial ({len(parsed)}/{len(batch)}), retrying...")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_sec = backoff[min(attempt, len(backoff)-1)]
                    print(f"  [Batch {idx}] Rate limit (429), waiting {wait_sec}s...")
                    time.sleep(wait_sec)
                else:
                    print(f"  [Batch {idx}] HTTP Error {e.code}: {e.reason}, retry {attempt+1}/4...")
                    time.sleep(2)
            except Exception as e:
                print(f"  [Batch {idx}] Request Error: {e}, retry {attempt+1}/4...")
                time.sleep(2)

        if success and parsed:
            # Update checkpoint
            for item in batch:
                if item["id"] in parsed:
                    checkpoint[item["id"]] = parsed[item["id"]]
            total_translated = len(checkpoint)
            
            # Save checkpoint
            with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False)

            elapsed = time.time() - start_time
            rate = total_translated / elapsed if elapsed > 0 else 0
            batch_dur = time.time() - batch_start
            print(f"[Batch {idx}/{len(batches)}] Done in {batch_dur:.1f}s | Progress: {total_translated}/{len(all_entries)} ({(total_translated/len(all_entries))*100:.1f}%) | Speed: {rate:.1f} items/s")
        else:
            failed_batches += 1
            print(f"[Batch {idx}/{len(batches)}] FAILED after retries. Skipping batch.")

        time.sleep(0.1)

    print("\n" + "="*50)
    print(f"Translation run completed in {time.time() - start_time:.1f}s")
    print(f"Total entries in checkpoint: {len(checkpoint)} / {len(all_entries)}")
    print(f"Failed batches: {failed_batches}")
    print(f"Checkpoint saved to {CHECKPOINT_PATH}")

if __name__ == "__main__":
    main()
