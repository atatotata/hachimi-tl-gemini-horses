# hachimi-tl-gemini-horses

The whole JP game in English for Hachimi. Fast, complete, and updated with the latest content.

## Quick Setup

Paste this into Hachimi's **Translations Meta URL**, pick your flavor, and update:
```
https://raw.githubusercontent.com/atatotata/hachimi-tl-gemini-horses/main/meta.json
```

## Flavors

- **Flagship**: Official Global text + exact skill math + AI gaps (Recommended).
- **Community**: Classic fan wording + skill numbers, zero Global text.
- **Lore**: Plain skill text without formulas/numbers (pure vibes).
- **Full-slim**: All text + daily UI pictures (~60 MB, snappy).
- **Full**: Everything above + all UI atlases, textures, and movie (~435 MB).

## Translation priority

- **Skill descriptions** (`cat48`): SD math > Global > UmaTL > Gemini.
- **Skill names** (`cat47`): Global > UmaTL > Gemini on Flagship; Community and Lore keep UmaTL names.
- **Trait names** (`cat147`): Global > UmaTL > Gemini on Flagship; Community and Lore keep UmaTL names.
- **Condition names and text** (`cat142` / `cat143`): Global > UmaTL > Gemini on Flagship; Community and Lore keep UmaTL.
- **Race commentary** (`race_jikkyo_*`): Global; already fully adopted.
- **Everything else**: Global > UmaTL > Gemini.

## Global sync

Flagship treats the official Global master as the source of truth whenever the same key also exists in the JP master.

- `cat48` skill descriptions are never overwritten; SD math wins.
- Global-only rows are skipped because JP has no matching key.
- Global stores line breaks as literal `\n`; adopted text converts them to real newlines.
- Rows that already match Global but carry our own wraps or `$(scale NN)` tags are kept as-is.
- `community` and `lore` stay on UmaTL for skill, trait, and condition names.

Preview an intake:

```
python tools/adopt_global_restore.py --dry-run
```

Write the repo and live Hachimi mirror:

```
python tools/adopt_global_restore.py --apply
python tools/adopt_global_cst.py --apply
```

Both scripts refuse to run outside `main`, `full`, and `full-slim`.

## Quick Tips

- **Upgrading & text/UI looks weird?** Delete `assets/textures`, `assets/atlas`, and `assets/movies` in your `hachimi/localized_data_N` folder (keep `includes_*`) and re-update.
- **Slow updater or manual install?** Grab the plug-and-play [release zips](https://github.com/atatotata/hachimi-tl-gemini-horses/releases/latest) with zero re-download required.
- **Switching flavors?** Just select another flavor in Hachimi's repo menu anytime.
