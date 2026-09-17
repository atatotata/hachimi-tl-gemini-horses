## 2026-09-17 -- Fix Error 102 (stale atlas manifests)
Removed 3 stale atlas diff PNGs (common, factorresearch, racecommon) whose dimensions no longer matched current JP meta after game update. Updated atlas JSON bundle hashes. Fixes Communication Error: Error 102 on full flavor.

## 2026-09-17 -- 100% master.mdb coverage
Filled all 1,414 previously-untranslated text_data rows (1,281 single-mode story titles in cat 181, 91 character lore in cat 92, 32 UI in cat 191, 8 scenario in cat 290, 2 counters in cat 355). Zero untranslated master rows remain.

## 2026-09-17 -- Global official EN home + lyrics
653 home voice timelines and 32 song lyric files overlaid from Global bundles. Home keeps 794 JP-only lines; 2 lyric-less songs keep repo placeholders.

## 2026-09-17 -- Global official EN career stories
8045 single-mode timelines overlaid from Global bundles (same chacha20 pipeline). Replaces Gemini JP career translations with official EN; 466 shared timeline IDs deduplicated.

## 2026-09-17 -- Global official EN stories
736 story timelines (main/event/chara, 37,836 lines) overlaid from Global bundles via libnative chacha20 33B key. Replaces Gemini JP translations with official EN where Global has released them.

# Changelog

## 2026-09-16 -- Fresh G/Download Log
- Translated 47 new UI bits from G:/Downloads/hachimi.log via gemini-3.7-flash-tiered -- FactorResearch reports, TrainerSkill abilities, SingleMode legacy sparks and more. Stars and placeholders verified.

## 2026-09-16 -- Fresh Global EN
- Harvested 1,607 text + 358 voice lines from the latest Global client (master 16.2 MB). Kept all Japan-only text and SD lore. SD bypass 1,122 preserved.

## 2026-09-12 — v8 Release Zips
- Fresh plug-and-play zips with the name cleanup, support titles, and all current menus. Verified zero-diffs again.

## 2026-09-12 — Horse Name Cleanup
- Fixed 25 misspelled horse names everywhere (T.M. Opera O, Rhein Kraft leftovers, Tanino Gimlet, Daring Tact, Curren family…). Cross-checked against JRA records, GameTora's index, and the Global client. Weekly syncs now enforce the spellings automatically.

## 2026-09-12 — Support Card & Story Titles Fix
- Filled in 1,541 missing titles across support cards, story chapters, and mini-events so you won't see blank headers anymore.
- Also added lore descriptions for 2 new skills and updated the pipeline so empty text won't slip through again.

## 2026-09-11 — Fresh Translations
- Translated 161 new UI bits like legal text, trainer skills, and plan sheets.

## 2026-09-11 — Fit Fixes
- Shortened over a dozen buttons and labels so text stops spilling out of boxes.
- Cleaned up terms like "Umamusume" across the board.

## 2026-09-11 — Training Plan + Skill Set Menus
- Translated 128 strings for the new Training Roadmap and Skill Set screens.
- Just update in-game and both menus will switch right to English.

## 2026-09-11 — v6 Release Zips
- Made fresh plug-and-play zips with everything up to the Phalaenopsis patch.

## 2026-09-11 — New Horse Phalaenopsis (1149)
- Translated 116 story scenes and 6 home lines for Phalaenopsis.
- Added 608 extra game strings from the same update.

## 2026-09-10 — Full Goes Entire
- Added the sprite sheets and the story movie (25,204 files, ~435 MB total).
- Let us know if training numbers look weird so we can adjust.

## 2026-09-10 — Racecourse Card Fix
- Shortened track names so they don't get cut off (like "Sapporo RC").

## 2026-09-10 — Hash Mismatch Fix
- Fixed the update hash error across 119,549 files.
- Just hit "Check for Updates" again and you're good.

## 2026-09-10 — Renamed to hachimi-tl-gemini-horses
- Renamed the project, so you will get one full re-download on your next update.

## 2026-09-10 — Plug-and-Play Release Zips
- Added v5 ready-to-use zips that won't make you re-download everything on setup.

## 2026-09-10 — Full Slim Flavor
- Added a `full-slim` version with text plus 214 core UI images (23,617 files, ~60 MB).

## 2026-09-10 — Full Flavor (Text + Pictures)
- Added a `full` pack with text and 1,723 translated pictures (25,126 files, ~390 MB).
- Needs an up-to-date Hachimi install to download without timing out.

## 2026-09-10 — Repos Don't Stack
- Clarified that you can only run one translation pack at a time in Hachimi.
- Use the included switcher file to easily swap between packs.

## 2026-09-10 — Dialogue Font Restored
- Brought back the custom dialogue font (3.6 MB) so text no longer looks generic.

## 2026-09-10 — Text-Only Fast Install
- Cut out heavy images to make the base pack super light (down to 23,401 files, ~38 MB).
- Release zips are now much smaller (~40 MB) and won't time out.

## 2026-09-07 — Lore Edition & Official Global Polish
- Added exact skill math to Flagship and a clean "Lore" version for story-only fans.
- Pulled in 54,000 official Global lines while keeping all Japan-only text intact.

## 2026-09-06 — 100% Story & Media Sweep
- Translated the last 4,200 cutscenes—every story in the game is now in English!
- Added 938 lobby chats, 1,200 race lines, and 25 songs, plus fixed text wrap.

## 2026-09-05 — Career Stories & Alignment Fix
- Added 14,136 career events and 395 card stories.
- Fixed dialogue choice positions and cleaned up character names.

## 2026-09-03 — Launch Day
- First launch with 94,000 strings, full voice lines, pictures, and PC/Android support.
