# Voice bible pipeline

Local-only tooling (the repo ignores `tools/`) that keeps a per-character voice
spec for translation prompts. Consumers: `tools/story_translate/translate_newstories.py`
and `tools/chara_fetch/batch_career50_pipeline.py` (they read `jp`, `en`,
`archetype`, `speech_tags`; `trainer_term` and `notes` are new, for prompt use).

## Files

| file | role |
|---|---|
| `canonical_voice.py` | Policy: shipped name fixes, trainer-address rules, tag denylist, hand-written voice notes with Global evidence. |
| `mine_voice.py` | Mines JP `character_system_text` + EN (Global first, ours second) into `voice_evidence.json`: pronouns, third-person self-reference, dialect-marker counts vs cast average, trainer-address lines with provenance, sample pairs. |
| `rebuild_voice_bible.py` | Merge-mode base build from JP `master.mdb` (cat 6 name, 144 trait, 182 reading) + our `text_data_dict` (Global cat6 wins). Preserves every enrichment field. Applies canonical name fixes, turns literal `\n` into real newlines, adds evidence tags. |
| `enrich_voice_bible.py` | LLM pass over OmniRoute (`antigravity/gemini-3.8-flash-tiered`, effort low, 16 entries/request). Prompt contains the mined evidence, so archetypes are grounded in dialogue instead of the character's name. Resume-safe (`voice_v`), `--force`, `--limit=N`. |
| `uma_voice_bible.json` | The bible: 174 entries keyed by character id. |

## Run order

```
python tools/voice_bible/mine_voice.py
python tools/voice_bible/rebuild_voice_bible.py
python tools/voice_bible/enrich_voice_bible.py            # only entries without voice_v=2
```

`rebuild_voice_bible.py` is idempotent: re-running it after enrichment changes
nothing. It must never be followed by a bare enrich without `--force` unless you
intend to keep the current archetypes.

## Policy encoded here

- **Global > UmaTL > house** (with the trainer-honorific exception below). Names
  and renders come from the Global master DB and the 9,230 harvested EN stories
  whenever a row exists.
- **NPC names are given-name-first** (`Kiyoko Hoshina`, `Mei Satake`, `Ryoka Tsurugi`,
  `Tazuna Hayakawa`, `Riko Kashimoto`), matching every NPC Global ships.
- **Akikawa is "Director Akikawa"**; Global has zero "Chairwoman" anywhere.
- **Character-unique trainer honorifics are preserved on the literal romaji `Tore-` stem**
  (user policy 2026-11-16, superseding the 2026-10 flatten-to-`Trainer` / `T-Rain` pass,
  enforced in CI by `tools/master_translate/guard_trainer_honorifics.py`):
  - `トレーナーさん` → `Tore-san`, `トレーナーさま/様` → `Tore-sama`,
    `トレーナーちゃん` → `Tore-chan`, `トレーナーくん/君` → `Tore-kun`,
    `トレーナー殿` → `Tore-dono`, `トレーナー先輩` → `Tore-senpai`.
  - **Daitaku Helios (`1065`)**: `トレぴ` → `Tore-pi`, `トレぴっぴ` → `Tore-pipi`,
    `トレぽよ` → `Tore-poyo`, `トレぴよ` → `Tore-piyo`, `ちゃんヘリ` → `Heliboss`,
    `DJトレーナー` → `DJ Trainer` (never Global's `T-Rain` or `DJ T-Rainster`, and
    never UmaTL's `Trai-pi`).
  - **Transcend (`1080`)**: `トレちゃん` → `Tore-chan` (elongated `トレちゃーん` → `Tore-chaaan`).
  - **Vivlos (`1091`)**: `トレっち` → `Tore-cchi` (`Tore-cchi-poo`).
  - **Durandal (`1121`)**: `我が王` → `my King`, `我が君` → `my liege`,
    `主`/`主君` → `my lord`, `トレーナー殿` → `Tore-dono`.
  - **Other established terms**: Rice Shower `お兄さま` → `Big Brother`,
    Curren Chan `お兄ちゃん` → `Big Bro`, Agnes Tachyon `モルモット` → `guinea pig`,
    Hishi Amazon `トレ公` → `Teach`, Tokai Teio `カイチョー` → `Prez`,
    Azuma `貴方様` → `my lord`.
  - **Plain `トレーナー`** (no honorific) and determiner/possessive role-noun uses
    (`my trainer`, `her trainer`, `a trainer`, `the trainer`) stay `Trainer`/`trainer`.
    Never use `Trainer-san/-sama/-chan/-kun/-dono/-senpai`, `T-Rain*`, `Trai-pi*`,
    `Trai-chan`, `Trainy*`, `Trainie`, or `Trainey`.

## Known limits

- Story dialogue is not mined yet. JP story text lives in the encrypted
  `Persistent/meta` + `dat` bundles; `extract_missing_storytimelines.py` can pull
  it per timeline id, and aligning those lines against our EN would let the miner
  cover characters whose `character_system_text` is thin (1142, 1148, 2001-2008,
  9007, 9045, 9051 have no lines at all).
- 23 entries have no trainer address because no cst line mentions one.
- The bible is untracked on every branch (the repo ignores `tools/`). Keep a copy
  outside the repo if it matters.
