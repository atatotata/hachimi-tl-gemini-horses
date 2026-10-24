# Changelog

## 2026-10-24 -- Global condition names and text
- Adopted 25 condition names and 27 descriptions from Global. All 27 conditions Global covers now match; the 22 JP-only ones keep their current text.
- Flagship only. Community and Lore stay on UmaTL.

## 2026-10-23 -- Global trait names
- Brought 1,044 trait names in line with Global. All 1,345 traits Global covers now match; the 1,211 JP-only ones keep their current translations.
- Flagship only. Community and Lore stay on UmaTL.

## 2026-10-23 -- Restore Global skill names on Flagship
- Restored 932 `cat47` skill names from before the UmaTL sync. Flagship is back to 1,110 exact Global names (all 1,122 once the 12 `$(scale)` prefixes are ignored) and 19 scale tags.
- `sync_umatl.py` no longer lets UmaTL overwrite Global-backed text on `main`, `full`, and `full-slim`; `cat48` stays SD math.
- `community` and `lore` keep their UmaTL skill names, and `sync_global.py` now skips `cat47` there.

## 2026-10-23 -- Fit the last Global titles and 45 voice lines
- Added the last 30 story titles and 1 song title from Global. Seven use `$(scale NN)` so they stay within the same width as before.
- Shrank 45 Global voice lines to 85–95% so they fit in 3 lines instead of 4–5.
- Fixed a small Global typo in `1099/91010`: `sp` -> `so`.
- 18 voice lines are still too long even at 85%, so they keep the old translation.
- index.json regenerated (23,673 files).

## 2026-10-21 -- Split 31 long shop labels (cat 39) to prevent card clipping
- Labels longer than 26 display columns are now two-line, preferring breaks before `★3`/`SSR` tokens (e.g. `2.5th Anniversary\n★3 Exchange Ticket`, `Half Anniversary\nSSR Support Card Exchange`).
- The 49-column Umabako ticket also carries `$(scale 85)` because a two-line split alone was still too wide.
- No wording changes; index.json regenerated (23,673 files).

## 2026-10-21 -- Restore shop-menu label line breaks (cat 39)
- The exchange menu labels lost the JP two-line layout (JP uses literal `\n`), so `Club Point Exchange` and friends clipped at the card edge.
- Rewrapped 11 labels to match JP segments (`Friend Point\nExchange`, `Club Point\nExchange`, `1st Anniv.\nCelebration`, ...) and normalized 4 `Carnival Pts` rows that still had a literal `\n`.
- No wording changes; index.json regenerated (23,673 files).

## 2026-10-21 -- Rewrap 380 tutorial rows (cat 63) to JP line structure
- Rebuilt tutorial `text_data` category 63 rows that had lost their JP line breaks (JP uses literal `\n`), using proportional line widths; also normalized stray literal `\n` inside EN bodies.
- Preserves existing `$(scale NN)` tags where present; no wording changes.
- 380 rows rewritten (382 total in cat 63, 104 still carry scale tags).
- index.json regenerated (23,673 files).

## 2026-10-21 -- Rewrap 11,444 character voice lines to match JP line structure
- For every `character_system_text` row where the JP original has 2-3 manual lines and our EN was one long line, re-wrapped the EN into the same number of lines using widths proportional to the JP line widths.
- Prevents the fixed-height voice bubbles from clipping the last line; no wording changes.
- index.json regenerated (23,673 files).

## 2026-10-21 -- Add `$(scale NN)` to 1,049 overflow-prone UI strings
- Tier 1 (955): short single-line labels (<=45 cols) where EN is 1.15-1.25x wider than JP; scaled to 85-98% (`localize` 54, `text_data` 772, `cst` 129).
- Tier 3 (94): tutorial `text_data` category 63 where EN exceeds the fixed box; scaled to 75-90%, including the Training Plan tutorial (`63/386`, 85%).
- Scaling chosen over rewrapping for tutorials because the overflow is vertical (extra lines would be clipped by the footer).
- Skipped `$(scale)` where the required size was below 75% (those need rewording, tracked separately).
- index.json regenerated (23,673 files).

## 2026-10-20 -- Adopt 113 official Global UI/menu strings + scale tags on compact labels
- Filled 113 `text_data` rows that existed only in the Global master (all outside the quarantined localize keys, so no Error 102 risk): racewear names (cat 14, 13), costume titles (cat 5, 2), story titles (cat 181, 60), mission/song text (cat 65, 10), level labels (cat 233, 5), event/result labels (cats 194/209/210, 14), live title (cat 283, 1), plus misc UI labels.
- Used the official Global EN wording (e.g. `MELTY GIFT` -> `Melt Your Heart`, `[Creeping Black]` -> `[Creeping Shadow]`, `Manticore`-class racewear names) instead of leaving the JP-English placeholder.
- Added `$(scale NN)` to the 6 adopted compact labels where EN is materially wider than JP (cats 5/14; NN clamped to 85-98) to avoid bounding-box overflow on card/button surfaces. Longer-form titles/labels were left untagged because scaling them below 85% would be unreadable.
- index.json regenerated (23,673 files).

## 2026-10-20 -- Unify "Cleats" wording in the exchange menu
- `Shop0149` button: `Exchange Horseshoes` -> `Exchange Cleats`; `Shop0129` -> `Cleats`; `Outgame0165` -> `...following cleats...` (matches the tutor bubble and official Global's "Cleats" term).
- Pinned all three in `sync_umatl.py` so the weekly UmaTL overlay keeps them (upstream still says "Horseshoes").

## 2026-10-20 -- Fix Horseshoe Exchange tutor bubble overflow
- The tutor bubble is a fixed multi-line JP label, but the official Global English (identical to ours) is one 109-char line, so it clipped to `Here, you can exchange excess Supp…`.
- Wrapped `character_system_text` 9001/`250000` and `250001` into 3 manual lines.
- Pinned both rows in `sync_global.py` so future Global syncs keep the line breaks (verified: drift is re-applied as `1 slot-fit pin`).

## 2026-10-19 -- Global Minor Sync
- Synced official English text and character voice lines from the latest Global update.
- Verified all story cutscenes, home screen dialogues, and live song lyrics remain fully up to date.

## 2026-10-13 -- Colored Story Text Fix
- Fixed highlighted text in ~4,800 story cutscenes reverting to Japanese.
- Translated over 1,500 highlighted terms (character names, race titles, terms) so text highlights now match English dialogue seamlessly.

## 2026-10-13 -- Halloween Duramente & JP Content Update
- Translated all new content from the JP update: Duramente's [Claret Nosferatu] Halloween costume story cutscenes and voice lines.
- Translated new skills, missions, story titles, and event text (including PakaLive TV & 7th Event Tour references).
- Synced the latest Global English text improvements.

## 2026-09-30 -- Race Commentary Update
- Translated new live race commentary lines for Phalaenopsis and Rose Kingdom's G1 victories.

## 2026-09-30 -- Event 1057: Demon Empress & Black Knight King
- Fully translated all 8 story chapters for the "Demon Empress & Black Knight King" fantasy story event.

## 2026-09-30 -- New Career & Event Stories
- Translated new story episodes for Gold City and Taiki Shuttle career modes.
- Added English dialogue for 4 new seasonal event cutscene groups.

## 2026-09-30 -- Character Voices & Game Text Update
- Translated new voice lines for Gold City, Taiki Shuttle, Mejiro Dober, Agnes Tachyon, Gentildonna, and more.
- Translated new skills, missions, story titles, character profiles, and UI text from the JP update.

## 2026-09-29 -- Release Packaging Improvements & Text v16
- Standardized release titles and download package filenames across all flavors.
- Cleaned up legacy release tags and published `Text v16` packages.
- Updated README download links for one-click manual installation.

## 2026-09-27 -- Anime Collaboration & Song Content
- Translated the *Umayuru: Full Gate!* anime login bonus lines and stories.
- Translated lyrics and text for *Round and Round: Tracen Days*, fan comments, and new story titles.

## 2026-09-26 -- Integrity & Build Checks
- Improved automated integrity checks to guarantee complete asset coverage and prevent missing or orphaned files in releases.

## 2026-09-26 -- UI Texture & Dialogue Polish
- Fixed a lingering Japanese phrase in home screen conversations.
- Added translated UI graphic overlays for Factor Research, common menus, and race screens to the Full flavor.

## 2026-09-26 -- Fix Error 102 Crash
- Resolved an issue causing in-game "Error 102" by preventing sensitive training schedule keys from sending translated strings to the server.

## 2026-09-26 -- Massive UI Translation Coverage
- Added and translated nearly 1,800 missing UI labels, buttons, and popups across the game menus.
- Ensured formatting tags, colors, and player-name placeholders display correctly without falling back to Japanese.

## 2026-09-26 -- Story Formatting & Choice Fixes
- Fixed a formatting bug in 90 story scenes that caused Hachimi to fall back to Japanese.
- Realigned interactive dialogue choices and colored text highlights across affected story cutscenes.

## 2026-09-25 -- Rose Kingdom Story Polish
- Translated all highlighted text spans across Rose Kingdom's story arc (race titles, academy terms, and character names).

## 2026-09-23 -- Dialogue Choice Alignment Fix
- Fixed dialogue choices appearing in Japanese during story events (including Taiki Shuttle's "Must-Win Match").
- Restored missing text highlights for race names and character titles.

## 2026-09-23 -- Linebreak Display Fix
- Fixed an issue where literal `\n` text was displayed on screen instead of actual linebreaks in dialogues and UI popups.
- Added automated guards to prevent raw newline escapes from shipping in future updates.

## 2026-09-23 -- Global Sync & Japanese Text Cleanup
- Translated remaining untranslated dialogue scenes, including Matikanetannhauser's birthday home interaction.
- Restored missing hot spring raffle event text highlights.
- Improved sync safeguards to ensure official English never overwrites existing translations with blank lines.

## 2026-09-19 -- Complete Story & Dialogue Choice Coverage
- Restored and translated over 72,000 interactive event choices across 8,000+ story cutscenes.
- Cleaned up remaining untranslated Japanese dialogue lines and character speaker names game-wide.
- Translated newly discovered UI elements reported from gameplay logs.

## 2026-09-18 -- Rose Kingdom Release & Full Package Fix
- Added full English support for new character Rose Kingdom (all story chapters and home screen voices).
- Translated new voice lines, skills, and titles from the game update.
- Fixed Full flavor downloads to include all UI graphic textures and movies properly.
- Added automated build validation and release workflows.

## 2026-09-17 -- Error 102 Fix & Major Global Sync
- Fixed a server disconnect (Error 102) caused by translated training schedule buttons.
- Synced thousands of official Global English career stories, home screen voice lines, and song lyrics.
- Replaced outdated UI textures and filled gaps in story titles, skill descriptions, and character lore.

## 2026-09-16 -- Global Text & UI Additions
- Synced over 1,900 official dialogue and voice lines from the latest Global game client.
- Translated Factor Research, Trainer Skills, and career mode UI elements.

## 2026-09-12 -- v8 Release
- Cleaned up character and support card names across all current menus.
- Standardized horse names across all translations.
- Translated live race commentary.
- Shipped distinct flavor branches: Flagship, Community, Lore, Full, and Full-slim.

## 2026-09-10 -- Sync System
- Built upstream sync system to merge UmaTL, Global EN, and Gemini translations while preserving exact skill numbers.
- Synced career mode and home screen dialogue from official Global English.

## 2026-09-06 -- 100% Story Coverage
- Translated the final 4,200 cutscenes -- every story cutscene in the game is now in English.
- Added 938 lobby chats, 1,200 race lines, and 25 songs.

## 2026-09-05 -- Career & Alignment
- Added translations for 14,136 career events and 395 support card stories.
- Fixed dialogue choice positions and cleaned up character names.

## 2026-09-03 -- Initial Launch
- First launch: 94,000 translated strings, full voice lines, translated UI pictures, with PC and Android support.
