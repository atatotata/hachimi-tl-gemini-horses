"""Add the three already-English keys from the 2026-10-24 JP update."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses")
LIVE = Path(r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\hachimi\localized_data_1")
ADD = {
    ("372", "9052"): "Azuma",
    ("150", "30322"): "Time of Departure",
    ("76", "30322"): "[Time of Departure]",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    paths = [REPO / "localized_data" / "text_data_dict.json"]
    if args.live:
        paths.append(LIVE / "text_data_dict.json")
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        added = 0
        for (cat, idx), value in ADD.items():
            data.setdefault(cat, {})
            if idx not in data[cat]:
                data[cat][idx] = value
                added += 1
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"{path}: added={added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
