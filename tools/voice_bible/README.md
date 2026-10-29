# Voice bible

Per-character voice spec for the translation prompts: who a character is, how they
speak, and how they address the trainer. It exists because early machine
translation produced lines that were grammatical but off-voice — Lucky Lilac
sounding like a princess instead of a Kansai girl, Helios addressed as
"Trainer-san" when Global calls her trainer "T-Rain", NPC plates reading
"Takeshi Hoshina" for a character named Kiyoko.

**Tracking status:** this directory is committed on all five branches. The repo
ignores `tools/*` with an explicit `!tools/voice_bible/` exception, so normal
`git add` works here. `voice_evidence.json` (regenerable, ~500 KB) and
`*.pre_v2.json` backups are ignored.

## Files

| file | role |
|---|---|
| `uma_voice_bible.json` | The bible: 174 entries keyed by character id. |
| `canonical_voice.py` | Single source of truth for the shipped-text rules: `NAME_FIXES`, `HONORIFIC_FIXES`, `SPEAKER_VOICE`, `TRAINER_TERMS`, `TAG_DENY`, `VOICE_NOTES`. |
| `mine_voice.py` | Mines JP `character_system_text` against EN (Global first, ours second) into `voice_evidence.json`: pronouns, third-person self-reference, dialect markers as a ratio against the cast average, trainer-address lines with provenance, and sample pairs. |
| `rebuild_voice_bible.py` | Merge-mode base build: JP `master.mdb` cat 6 (name), cat 144 (trait), cat 182 (reading) + our `text_data_dict` (Global cat 6 wins). Preserves every enrichment field, applies `NAME_FIXES`, converts literal `\n` into real newlines, attaches evidence tags. Idempotent. |
| `enrich_voice_bible.py` | LLM pass over OmniRoute (`antigravity/gemini-3.8-flash-tiered`, effort low, 16 entries per request, temperature 0.2). The prompt includes the mined evidence, so archetypes describe how the character actually talks. Resume-safe via `voice_v`; supports `--force`, `--limit=N`. |
| `voice_evidence.json` | Generated, ignored. Delete it and re-run `mine_voice.py` any time. |

## Entry schema

```json
"1065": {
  "jp": "ダイタクヘリオス",
  "en": "Daitaku Helios",
  "reading": "ダイタクヘリオス",
  "trait_jp": "…", "trait_en": "…",
  "archetype": "frenetic, slang-spewing party girl who treats racing like a festival",
  "speech_tags": ["gyaru-slang", "energetic", "third-person-self"],
  "trainer_term": "T-Rain",
  "notes": "Gyaru register; トレぴ is Global's T-Rain; spells her own name in katakana.",
  "voice_v": 3
}
```

- `voice_v: 3` means "enriched from mined evidence". `enrich_voice_bible.py`
  skips entries at the current version unless `--force` is passed.
- `trainer_term` is how the character addresses the trainer (`Trainer`, `T-Rain`,
  `Big Bro`, `Big Brother`, `Teach`, `my lord`, or empty when no line exists).
- Consumers (`translate_newstories.py`, `batch_career50_pipeline.py`,
  `merge_supp_career.py`) read `jp`, `en`, `archetype`, `speech_tags`, and now
  `trainer_term` / `notes`.

## Policy

Priority is **Global > UmaTL > house coinage**. Global means the EN master DB
(`text_data`, `character_system_text`) plus the 9,230 harvested EN stories in
`tools/umamusu-utils/storage/story_global`.

### Names

NPC personal names are given-name-first, which is what Global ships for every NPC
it has:

| id | was | now | evidence |
|---|---|---|---|
| 9001 | Hayakawa Tazuna | **Tazuna Hayakawa** | Global plateau 1,427 |
| 9002 | Chairwoman Akikawa | **Director Akikawa** | Global 1,333 plates, 0 "Chairwoman" |
| 9003 | Reporter Otonashi | **Etsuko Otonashi** (plate stays "Reporter Otonashi") | Global cat 6 |
| 9006 | Kashimoto Riko | **Riko Kashimoto** | Global 733 plates |
| 9043 | Satake Mei | **Mei Satake** | no Global row, UmaTL cat 6 |
| 9044 | Tsurugi Suzuka / Tsurugi Ryoka | **Ryoka Tsurugi** | 涼花 is Ryoka, not Suzuka |
| 9050 | Takeshi / Keiko / Kenko / Takeko Hoshina | **Kiyoko Hoshina** | furigana ホシナキヨコ |
| 2006 | Rigauntona | **Rigantona** | repo cat 6, UmaTL |

### Honorifics

Global uses **zero** Japanese honorifics: `-chan`, `-kun`, `-dono`, `-sama`,
`-senpai` all return 0 hits in `text_data`, `character_system_text`, and the
harvested stories (the single `-chan` hit is "World-Changing Darjeeling").
Consequently `Trainer-san`, `Trainer-chan`, `Trainer-kun`, `Trainer-dono` and
`Trainer-sama` are retired to plain `Trainer`. Maruzensky's Global row proves it:
`ありがと、トレーナーちゃん♪` → "Thank you, Trainer! ♪".

### Character-specific renders

| character | JP | EN | source |
|---|---|---|---|
| Daitaku Helios | トレぴ | **T-Rain** | Global `text_data` 232/347, 232/575, 185/1065 |
| Daitaku Helios | ちゃんヘリ | **Heliboss** | Global 185/1065, 228/183 |
| Daitaku Helios | DJトレーナー | **DJ T-Rainster** | Global 205/978, 205/980 |
| Daitaku Helios | トレぴっぴ | **T-Rain-pi** | house (affectionate diminutive) |
| Transcend | トレちゃん | **Trainer** | no Global row; 8 house variants collapsed |
| Durandal | 我が王 | **my King** | no Global row; chapter titles already used it |
| Durandal | 我が君 | **my liege** | knight register, dominant existing form |
| Durandal | 主 / 主君 | **my lord** | distinguishes from 我が王 |
| Durandal | トレーナー殿 | **Trainer** | Global drops 殿 for Yaeno: "Face Trainer, bow!" |
| Azuma | 貴方様 / トレーナー様 | **my lord** | matches Global's wording of her cst line |
| Curren Chan | お兄ちゃん | **Big Bro** | Global 27/48 |
| Rice Shower | お兄さま | **Big Brother** | Global 34/37 |
| Hishi Amazon | トレ公 | **Teach** | Global 16/17 |
| Agnes Tachyon | モルモット | **guinea pig** | Global 8/8 |

Deliberate exceptions:

- **Vivlos (1091)** coins "Trainy" / "Trainy-poo" herself in dialogue. It is a
  nickname she invents, not a honorific, so it stays.
- **`501031304`** has two player-choice strings, "Wait, Trainer-kun...?" and
  "Wait, Trainer-chan...?". They are parallel variants of one line; collapsing
  both would show the player two identical choices, so they keep the suffix.

### Speech tags

Tags come from mined evidence, not guesses: `kansai`, `hokkaido`, `tohoku`,
`katakana-english`, `ojou-desuwa`, `archaic-register`, `gyaru-slang`,
`third-person-self`, `rough`, `keigo`, `polite`, `earnest`, `formal`,
`energetic`, `casual`.

A tag is only applied when the marker count clears a floor *and* a multiple of the
cast average. `TAG_DENY` in `canonical_voice.py` blocks known false positives
(e.g. `おる` read as Kansai when it is plain "to be", `あげ` read as gyaru). If a
tag looks wrong, fix the lexicon in `mine_voice.py` and re-run — do not hand-edit
the JSON, the next rebuild will overwrite it.

## Running the pipeline

```bash
# 1. Mine evidence (read-only against the game DBs)
python tools/voice_bible/mine_voice.py

# 2. Rebuild the base bible (merge mode: keeps every enriched field)
python tools/voice_bible/rebuild_voice_bible.py

# 3. Enrich new/changed entries only
python tools/voice_bible/enrich_voice_bible.py
python tools/voice_bible/enrich_voice_bible.py --force          # re-do all 174
python tools/voice_bible/enrich_voice_bible.py --limit=16       # smoke test
```

Order matters: `rebuild` after `enrich` must change nothing (idempotency check);
if it does, the merge logic has a bug.

### API key

`enrich_voice_bible.py` reads the OmniRoute key from `OMNIROUTE_API_KEY` or
`VISION_BRIDGE_API_KEY` in the environment, then `~/.omniroute/.env`,
`E:\AI_Offload\.omniroute\.env`, or `<repo>/.omniroute/.env`. There is no
hardcoded fallback — this tree was published once, so keys never live in code.

## Applying the policy to shipped text

`canonical_voice.py` holds the rules; `E:\AI_Offload\TMP\opencode\normalize_voice.py`
applies them. It parses each JSON, rewrites only the matching strings, and
re-dumps with the per-file indent that reproduces the original byte-for-byte
(0 fallbacks on the 2026-10-28 run). Speaker-scoped rules only fire inside that
character's own `text_block_list` entries or `character_system_text` rows, which
is what protects Vivlos and Loves Only You.

After any bulk text edit:

```bash
python tools/master_translate/guard_excluded_keys.py      # 9,874 keys, 0 excluded
python tools/master_translate/guard_literal_newlines.py   # no literal \n in localize/story
python sync_umatl.py --regen-index                        # rebuild index.json
```

Then commit on `main`, and for each of `full`, `full-slim`, `community`, `lore`:
checkout, `python sync_umatl.py --regen-index`, commit, push. Mirrors:
`robocopy localized_data ..\hachimi\localized_data_1 /MIR`.

## Consumers

- `tools/story_translate/translate_newstories.py` — builds the
  "CHARACTER VOICE BIBLE" prompt block from `en`, `archetype`, `speech_tags`,
  and pre-resolves speaker plates through the bible's `jp` → `en` map.
  `BIBLE_PATH` is repo-relative and a missing/empty bible is fatal: a silent `{}`
  used to drop the whole voice block and nobody noticed.
- `tools/chara_fetch/batch_career50_pipeline.py` — same block, plus `trainer_term`
  for trainer address. Local-only file.
- `tools/chara_fetch/merge_supp_career.py` — uses the bible only to pre-resolve
  canonical NPC names before merging. Local-only file.

## Known limits

- Story dialogue is not mined. JP story text sits in the encrypted
  `Persistent/meta` + `dat` bundles; `extract_missing_storytimelines.py` can pull
  it per timeline id, and aligning those lines with our EN would cover characters
  whose `character_system_text` is thin (1142, 1148, 2001-2008, 9007, 9045, 9051
  have no lines at all).
- 25 entries have no trainer address because no cst line mentions one.
- `trait_en` / `trait_jp` are stored for reference but no consumer reads them; 137
  of them are older than the current Global text.
- Global's own Helios character story (04/1065) is not in the harvest (145 of 148
  timelines missing), so her long-form dialogue cannot be checked against Global.
  The short-form `text_data` rows above are the evidence.
- The bible is a snapshot, not a live feed: after a game update run
  `mine_voice.py` + `rebuild_voice_bible.py` before translating new content.
