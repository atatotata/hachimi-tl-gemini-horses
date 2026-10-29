# hachimi-tl-gemini-horses

The whole JP game in English for Hachimi. Fast, complete, and updated with the latest content.

## Quick Setup

Paste this into Hachimi's **Translations Meta URL**, pick your flavor, and update:
protip: pick the [SLOW] one, it has everything.
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
- **Everything else**: Global > UmaTL > Gemini.

## Voice and naming

Characters keep their official voice. The translation prompts carry a per-character
voice bible (archetype, speech tags, how they address the trainer), so slang,
dialect and register survive the trip through English instead of flattening out.

- NPCs use given-name-first order, as Global does: Tazuna Hayakawa, Director Akikawa, Kiyoko Hoshina.
- No Japanese honorifics: the trainer is plain "Trainer", never "Trainer-san", "Trainer-chan" or "Trainer-dono".
- Character-specific forms follow Global where it exists: Helios calls you "T-Rain", Rice Shower says "Big Brother", Agnes Tachyon says "guinea pig".
- Where Global has no line yet, the house rendering is written down: Durandal uses "my liege" / "my King" / "my lord", Transcend uses "Trainer"; Azuma says "my lord".

The policy and its evidence live in [`tools/voice_bible/`](tools/voice_bible/README.md).
The same rules are re-applied on every upstream sync, so a merge cannot silently
undo them.

## Quick Tips

- **Upgrading & text/UI looks weird?** Delete `assets/textures`, `assets/atlas`, and `assets/movies` in your `hachimi/localized_data_N` folder (keep `includes_*`) and re-update.
- **Slow updater or manual install?** Grab the plug-and-play [release zips](https://github.com/atatotata/hachimi-tl-gemini-horses/releases/latest) with zero re-download required.
- **Switching flavors?** Just select another flavor in Hachimi's repo menu anytime.
