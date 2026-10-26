# Changelog

## 2026-10-26 -- Tutorial text repair and fit
- Restored the tutorial pages after the last reflow broke their color tags.
- Rescaled and rebalanced the 11 scenario pages so each fills its box evenly.

## 2026-10-26 -- UI scaling tweaks
- Re-broke and scaled the skill-hint tip so it fits its box.

## 2026-10-26 -- Teaching Impartation scaling
- Scaled the program names across the cards and level lists.
- Shrank the Program Lv. List label so it fits its circle.
- Scaled the Lead Effects List button.
- Fit the Horsegirl Details tab.

## 2026-10-26 -- Error 102 guard
- Removed the 12 schedule keys that the upstream sync brought back.
- Sync now filters those keys so they cannot return.
- CI pins the 13-key exclusion list, and release builds reject any branch that contains one.

## 2026-10-26 -- Restore Global text after upstream sync
- Restored the rows the latest upstream sync overwrote, keeping Global wording first.

## 2026-10-26 -- Scenario phase headers
- Translated the Junior and Classic late-December phase headers.

## 2026-10-26 -- Teaching List fit
- Translated the Debut phase header and scaled the Transmuted and Teaching Effect buttons.

## 2026-10-26 -- Teaching Impartation fit
- Shortened the Horsegirl Details and Performance Lead labels so they stop overlapping.
- Scaled the program card names and Lead Effects List button to fit their columns.

## 2026-10-26 -- Confirm Transmutation fit
- Scaled the transmutation effect cards and confirmation line so they stay inside their boxes.

## 2026-10-26 -- Teaching Set labels
- Shortened the Teaching labels and scaled two long program names so the columns and chips fit.

## 2026-10-26 -- Transmutation screen fit
- Added the missing Transmutation Effect List title.
- Scaled the Teaching names and long effect text so the cards no longer overlap or clip.

## 2026-10-26 -- Scenario UI and story fixes
- Added 77 missing scenario menu strings from the Hachimi log. Left out the one Error-102 key.
- Added 11 more scenario menu strings found in a second log pass.
- Fixed 14 new story files where color-text entries were objects instead of strings; Hachimi can read them now.

## 2026-10-25 -- New JP scenario and support stories
- Translated 794 new text strings and 53 voice lines from the October JP update.
- Added 82 missing story timelines for the Goshiki Shuntaisai scenario and support cards, including the scenario prologue, choices, and color names.
- New terms use Goshiki Shuntaisai, Shuntaisai, and Azuma.
- Full audit found no untranslated story text. One leftover Japanese dash mark was replaced.
- Reflowed the five scenario program descriptions and set $(scale 85) so they fit the Details panel.
- Refit the 11 new scenario tutorial pages so their text fits the popup.
- All flavors get the new JP content. Flagship keeps Global wording for existing text.

## 2026-10-25 -- Global text and voice cleanup
- Put back 23,949 text entries that already matched Global before the UmaTL sync replaced them. Added 458 missing entries that both JP and Global have.
- Matched 39 voice lines to Global, wrapped to three lines or fewer. The Horseshoe Exchange keeps its Cleats wording.
- Race commentary already matched Global, so nothing changed.
- Flagship only. Community and Lore stay on UmaTL.

## 2026-10-24 -- Global condition names and text
- Matched 25 condition names and 27 descriptions to Global. All 27 conditions Global has now match; the 22 JP-only ones keep their current text.
- Flagship only. Community and Lore stay on UmaTL.

## 2026-10-23 -- Global trait names
- Matched 1,044 trait names to Global. All 1,345 traits Global has now match; the 1,211 JP-only ones keep their current names.
- Flagship only. Community and Lore stay on UmaTL.

## 2026-10-23 -- Global skill names on Flagship
- Restored 932 skill names to Global wording. Flagship now has 1,110 exact matches, or 1,122 once scale tags are ignored, with 19 scale tags.
- The UmaTL sync can no longer overwrite Global text on Flagship. Skill descriptions still keep exact SD math.
- Community and Lore keep their UmaTL names, and the Global sync skips skill names there.

## 2026-10-23 -- Last Global titles and voice lines
- Added the last 30 story titles and 1 song title from Global. Seven use scale tags to keep their old width.
- Shrank 45 Global voice lines to 85-95% so they fit in three lines instead of four or five.
- Fixed the Global "sp" typo in 1099/91010. Eighteen lines were still too long at 85%, so they keep the old text.

## 2026-10-21 -- Long shop labels
- Split 31 long shop labels over 26 columns into two lines, breaking before stars and rarity tags where possible.
- The 49-column Umabako ticket also uses scale 85.
- No wording changes. Index regenerated.

## 2026-10-21 -- Shop menu line breaks
- Restored the JP two-line layout for 11 exchange labels so they stop clipping.
- Fixed four Carnival Pts rows that still had a literal `\n`.
- No wording changes. Index regenerated.

## 2026-10-21 -- Tutorial row rewraps
- Rebuilt 380 tutorial rows with the same line structure as JP, using proportional widths.
- Kept the existing scale tags. No wording changes.
- Index regenerated.

## 2026-10-21 -- Character voice rewraps
- Rewrapped 11,444 character voice lines to two or three lines, matching the JP layout so the last line no longer clips.
- No wording changes. Index regenerated.

## 2026-10-21 -- Scale tags for wide UI
- Added scale tags to 1,049 UI strings that were too wide: 955 short labels at 85-98%, and 94 tutorial rows at 75-90%.
- Left rows that would need below 75% for a later rewording pass.
- Index regenerated.

## 2026-10-20 -- Global UI strings
- Filled 113 UI and menu strings from Global, including racewear, costumes, story titles, missions, level labels, and event text.
- Used official Global names instead of JP-English placeholders, such as MELTY GIFT becoming Melt Your Heart.
- Added scale tags to six compact labels. Longer titles were left unscaled.
- Index regenerated.

## 2026-10-20 -- Exchange currency as Cleats
- Changed the exchange menu to use "Cleats": Exchange Cleats, Cleats, and "following cleats".
- Pinned the three strings so UmaTL updates keep them.

## 2026-10-20 -- Horseshoe Exchange tutor bubble
- Wrapped the Horseshoe Exchange tutor bubble into three lines so it stops clipping.
- Pinned both lines so Global syncs keep the breaks.

## 2026-10-19 -- Global sync
- Adopted the latest Global text and voice lines: 89 UI strings and 240 voice lines.
- Checked story cutscenes, home dialogues, and song lyrics. All up to date.

## 2026-10-13 -- Colored text in story scenes
- Fixed colored text in about 4,800 story scenes that was still falling back to Japanese.
- Translated over 1,500 highlighted terms so they match the English dialogue.

## 2026-10-13 -- Duramente Halloween update
- Translated Duramente's Halloween costume story and voice lines.
- Added the new skills, missions, story titles, and event text from the JP update.
- Synced the latest Global improvements.

## 2026-09-30 -- Race commentary
- Added English for the new Phalaenopsis and Rose Kingdom G1 victory calls.

## 2026-09-30 -- Demon Empress & Black Knight King event
- Translated all eight chapters of the Demon Empress & Black Knight King event.

## 2026-09-30 -- Career stories
- Added Gold City and Taiki Shuttle career episodes.
- Translated four new seasonal event scenes.

## 2026-09-30 -- New voices and UI
- Added voice lines for Gold City, Taiki Shuttle, Mejiro Dober, Agnes Tachyon, Gentildonna, and others.
- Translated new skills, missions, titles, profiles, and UI text.

## 2026-09-29 -- Release cleanup
- Standardized release titles and download filenames across flavors.
- Cleaned up old tags and published the Text v16 packages.
- Updated the README download links.

## 2026-09-27 -- Umayuru and song update
- Translated the Umayuru: Full Gate! login bonus lines and stories.
- Added lyrics and text for Round and Round: Tracen Days, plus fan comments and story titles.

## 2026-09-26 -- Release checks
- Added integrity checks to catch missing or orphaned files before release.

## 2026-09-26 -- UI cleanup
- Fixed a Japanese line in home conversations.
- Added translated UI overlays for Factor Research, common menus, and race screens to Full.

## 2026-09-26 -- Error 102 fix
- Fixed Error 102 by keeping translated training schedule keys out of server payloads.

## 2026-09-26 -- Missing UI pass
- Added about 1,800 missing UI labels, buttons, and popups.
- Kept colors, tags, and player-name placeholders intact.

## 2026-09-26 -- Story fallback fix
- Fixed 90 story scenes that fell back to Japanese.
- Realigned choices and colored text in the affected scenes.

## 2026-09-25 -- Rose Kingdom highlights
- Translated the highlighted text in Rose Kingdom's story: race titles, academy terms, and names.

## 2026-09-23 -- Story choices
- Fixed Japanese choices in story events, including Taiki Shuttle's Must-Win Match.
- Restored missing highlights for race names and character titles.

## 2026-09-23 -- Line break fix
- Fixed literal `\n` text showing on screen instead of line breaks.
- Added checks to stop raw newline escapes from shipping.

## 2026-09-23 -- Global dialogue
- Translated the remaining dialogue, including Matikanetannhauser's birthday scene.
- Restored the hot spring raffle highlights.
- Sync now ignores empty Global lines so they cannot wipe existing text.

## 2026-09-19 -- Event choices
- Restored and translated over 72,000 event choices across 8,000+ scenes.
- Cleaned up remaining Japanese dialogue and speaker names.
- Added UI text found in gameplay logs.

## 2026-09-18 -- Rose Kingdom update
- Added full English for Rose Kingdom: story chapters and home voices.
- Translated the update's new voices, skills, and titles.
- Fixed Full downloads missing UI textures and movies.
- Added build checks and release workflows.

## 2026-09-17 -- Global sync and Error 102
- Fixed Error 102 caused by translated training schedule buttons.
- Synced thousands of Global career stories, home voices, and song lyrics.
- Replaced outdated UI textures and filled gaps in titles, skill text, and lore.

## 2026-09-16 -- Global dialogue and career UI
- Synced over 1,900 Global dialogue and voice lines.
- Translated Factor Research, Trainer Skills, and career UI.

## 2026-09-12 -- Name cleanup and release flavors
- Cleaned up character and support card names.
- Standardized horse names.
- Translated live race commentary.
- Split releases into Flagship, Community, Lore, Full, and Full-slim.

## 2026-09-10 -- Sync system
- Built the sync system for UmaTL, Global, and Gemini while keeping exact skill numbers.
- Synced career and home dialogue from Global.

## 2026-09-06 -- Story completion
- Finished the last 4,200 cutscenes. Every story is now in English.
- Added 938 lobby chats, 1,200 race lines, and 25 songs.

## 2026-09-05 -- Career and support stories
- Added 14,136 career events and 395 support card stories.
- Fixed choice positions and cleaned up character names.

## 2026-09-03 -- First release
- Released 94,000 translated strings, full voice lines, translated UI pictures, and PC/Android support.
