"""Parse MonsterHunterWorldModding Armor IDs wiki markdown export into JSON."""
import json
import re
import subprocess
import sys
from pathlib import Path


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not src or not src.is_file():
        print("Usage: parse_armor_wiki_md.py <Armor-IDs.md>", file=sys.stderr)
        sys.exit(1)
    out = Path(__file__).resolve().parent.parent / "data" / "armor_ids.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    # | 20                            | Rathian               | pl021\_0000               |
    row_re = re.compile(
        r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^\s|][^|]*?)\s*\|\s*$"
    )
    for line in src.read_text(encoding="utf-8", errors="replace").splitlines():
        m = row_re.match(line.strip())
        if not m:
            continue
        aid, name, model = m.groups()
        name = name.strip()
        model = model.strip().replace(r"\_", "_")
        if model.lower() == "none":
            model = None
        rows.append({"id": int(aid), "name": name, "model_path": model})
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {out}")
    merge = Path(__file__).resolve().parent / "merge_armor_i18n.py"
    if merge.is_file():
        subprocess.run([sys.executable, str(merge)], check=False)


if __name__ == "__main__":
    main()
