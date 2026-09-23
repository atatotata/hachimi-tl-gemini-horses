# Changelog

## 2026-09-23 -- Global sweep + last JP gaps closed
- Wider Global bundle sweep: paddock/announce/gacha/banner/tutorial buckets checked (Texture2D-only or no-dat; no adoptable text).
- Translated the last fully-JP home timeline (Matikanetanhoisa birthday, 22 strings) via OmniRoute.
- Added 14 color_text_info_list spans to story 50/1087 raffle (Hot Spring Voucher, Tracen Academy, itemname highlights) from decrypted JP bundle.
- Guarded sync_global.py against empty Global text rows (prevents blanking good EN).
- Repo-wide real-JP rescan: 0 remaining (2 intentional glosses: kaomoji EN, nukabed term).

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
