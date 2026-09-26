# Changelog

## 2026-09-26 -- Drop Error 102 keys from localize_dict
- Removed the 13 `SingleMode418025`-`SingleMode418037` keys that the CI guard rejects (they trigger in-game "Error 102"). These were re-introduced by the localize backfill; `localized_data/localize_dict.json` is now 9,762 keys.
- Repo and Hachimi mirror kept byte-identical. index.json regenerated.

## 2026-09-26 -- Backfill 1,795 missing localize keys
- Added the 1,795 game localize keys present in the game's localize dump (9,748 keys) but absent from `localized_data/localize_dict.json` (was 7,980 keys, now 9,775), so in-game UI strings that were falling back to Japanese now resolve.
- Translated ~1,290 Japanese values via the master.mdb JP->EN map + OmniRoute (batched, checkpointed), preserving `\n`, `<color=#RRGGBB>...</color>`, `<atlas=.../>` and `{0}` placeholders; 505 format-only/placeholder values kept verbatim; 15 reused from upstream UmaTL EN.
- Verified: 0 untranslated Japanese values remain; repo and Hachimi mirror byte-identical. index.json regenerated.

## 2026-09-26 -- Fix Hachimi story parse errors & rebuild choice/color placement
- Fixed 90 story files whose `color_text_info_list` used object entries (`{text,font_color}` / `{Text,FontColor}`) instead of Hachimi's required plain string array; Hachimi rejected the whole file (`invalid type: map, expected a string`) and fell back to Japanese.
- Rebuilt `choice_data_list` / `color_text_info_list` placement from the game bundles for 54 story files (each array placed at repo block index = bundle block - 1; the prior fix had duplicated/misaligned entries), translating all values to English (357 JP choices, 25 JP color spans) via the master.mdb JP->EN map plus OmniRoute for the 22 stragglers.
- Verified: 0 object-form color entries and 0 Japanese choice/color strings remain across all 22,084 story files; repo and Hachimi mirror are byte-identical for all 144 touched files. index.json regenerated.

## 2026-09-25 -- Rose Kingdom (1144) color spans translated
- Translated 67 unique Japanese color_text_info_list strings (78 spans across 34 files) in the Rose Kingdom arc (assets/story/data/50/1144) - race names, character names and racing terms (Japanese Derby, Satsuki Sho, Tracen Academy, Rose Clan, Umasta/Umatok/etc.).
- Reused authoritative master.mdb JP->EN for 48 strings, translated the remaining 19 via OmniRoute, and matched every span to the exact highlighted substring in the already-English block text.
- Verified: 0 genuine Japanese color spans remain in 1144. index.json regenerated (34 entries).

## 2026-09-23 -- Fix off-by-one choice/color alignment (JP choices regression)
- Root cause: choice restoration wrote EN choices at raw bundle indices, but Hachimi/game look them up at repo indices (repo dropped the empty first bundle block) => 'choice data not found in dict' => game fell back to JP.
- Moved 129 choice/color entries down by 1 index across 45 files (incl. Taiki Shuttle 'Must-Win Match' 501010514).
- Filled 58 missing color_text_info_list spans from decrypted JP bundles across 32 files and translated 54 unique span strings (race/character names) via OmniRoute.
- Verified: 0 JP choices / 0 JP color spans across all 70 touched files.

## 2026-09-23 -- Fix literal backslash-n rendering as text
- Converted 10 localize_dict keys (incl. Character701042 factor-spec dialog) from literal \n to real newlines - these rendered as visible "\n\n" in game.
- Converted 78 story/home timeline files (253 fields) with the same literal-\n defect.
- Left text_data_dict/cst/race_jikkyo/lyrics untouched: game-master files intentionally use literal \n (JP/Global master format, game converts at render).
- Added tools/master_translate/guard_literal_newlines.py (check + --fix) and wired into pre-commit hook.

## 2026-09-23 -- Global sweep + last JP gaps closed
- Wider Global bundle sweep: paddock/announce/gacha/banner/tutorial buckets checked (Texture2D-only or no-dat; no adoptable text).
- Translated the last fully-JP home timeline (Matikanetanhoisa birthday, 22 strings) via OmniRoute.
- Added 14 color_text_info_list spans to story 50/1087 raffle (Hot Spring Voucher, Tracen Academy, itemname highlights) from decrypted JP bundle.
- Guarded sync_global.py against empty Global text rows (prevents blanking good EN).
- Repo-wide real-JP rescan: 0 remaining (2 intentional glosses: kaomoji EN, nukabed term).

## 2026-09-19 -- Deep story & choices sweep (100% complete)
- Restored 72,668 missing event choice options directly from decrypted JP asset bundles across 8,176 story timelines.
- Translated 78,967 unique Japanese strings (dialogue lines, choice buttons, speaker names) via OmniRoute.
- Cleaned up all untranslated Japanese dialogue choices and character names across all 22,084 story files in repo.
- Translated remaining UI keys in `localize_dict.json` and 88 fresh `hachimi.log` keys.

## 2026-09-18 -- Rose Kingdom update & Full package fix
- New character Rose Kingdom (1144): 119 story timelines + 7 home voices translated.
- 463 new master.mdb strings covered (voice lines, titles, skills, UI).
- 100% master.mdb coverage confirmed.
- Fixed Full branch index: restored all 1,760 media files (506 MB / ~435 MB ZIP) so Full package selection downloads all UI pictures and movies.
- Added GitHub Actions CI validation, auto-release workflow, and pre-commit hook.

## 2026-09-17 -- Error 102 fix
- 13 schedule UI keys excluded from localize_dict (Load, Save, Schedule, etc.). Game was sending English text to server and getting rejected. 7,887 keys remain.
- Removed stale atlas PNGs that broke full flavor. Updated bundle hashes.
- Filled 1,414 untranslated text_data rows (story titles, lore, UI, skills). Zero untranslated master rows left.
- 653 home voice timelines and 32 song lyrics overlaid from Global EN.
- 8,045 career story timelines pulled from Global EN.
- 736 story timelines (main/event/chara) pulled from Global EN via decrypted meta.
- Global meta decrypted offline using Frida-captured chacha20 key (33 bytes). No game process needed.

## 2026-09-16 -- Fresh updates
- 1,607 text + 358 voice lines from latest Global client.
- 47 UI bits translated from hachimi.log (FactorResearch, TrainerSkill, SingleMode).

## 2026-09-12 -- v8 release
- Name cleanup, support titles, all current menus. Verified zero-diffs.
- Pinned horse names across all translations (12k hits checked, 0 wrong forms).
- Race jikkyo (live commentary) translated.
- Branches: main (flagship), community, lore (story-only), full (everything + media), full-slim (text + select UI images).

## 2026-09-10 -- Sync system
- UmaTL upstream sync system: merges UmaTL, Global EN, and Gemini translations with SD preservation.
- Career mode synced from Global EN.
- Home screen synced from Global EN.

## 2026-09-06 -- 100% story coverage
- Last 4,200 cutscenes translated -- every story in the game is now in English.
- 938 lobby chats, 1,200 race lines, 25 songs added. Text wrap fixed.

## 2026-09-05 -- Career & alignment
- 14,136 career events and 395 card stories added.
- Dialogue choice positions fixed, character names cleaned up.

## 2026-09-03 -- Launch
- First launch: 94,000 strings, full voice lines, pictures, PC/Android support.
