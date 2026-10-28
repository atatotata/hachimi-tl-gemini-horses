# Hardcoded UI asset patches

A few labels are baked into Unity assets and cannot be changed through
`localize_dict.json` or `text_data_dict.json`.

## Required Program Lv.

`必要演目Lv` exists three times in:

`UmamusumePrettyDerby_Jpn_Data/resources.assets`

The patch replaces it with `Required Lv.  ` (same 14-byte length) so the
serialized asset layout does not change.

### Usage

Close the game first, then run from the repository root:

```powershell
python tools/asset_patch/patch_required_lv.py --check
python tools/asset_patch/patch_required_lv.py --apply
```

The original is backed up beside the asset as:

`UmamusumePrettyDerby_Jpn_Data/resources.assets.bak_requiredlv`

To undo the patch:

```powershell
python tools/asset_patch/patch_required_lv.py --restore
```

Game updates replace `resources.assets`; rerun `--apply` after an update.
Do not commit the 278 MB asset or its backup to Git.
