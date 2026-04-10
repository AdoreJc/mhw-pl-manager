"""Load armor ID table (wiki export)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "armor_ids.json"


@dataclass(frozen=True)
class ArmorEntry:
    id: int
    name: str
    model_path: str | None
    name_zh: str | None = None
    name_ja: str | None = None


@lru_cache
def load_armor_entries() -> tuple[ArmorEntry, ...]:
    if not DATA_FILE.is_file():
        return ()
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return tuple(
        ArmorEntry(
            id=int(r["id"]),
            name=str(r["name"]),
            model_path=r.get("model_path"),
            name_zh=r.get("name_zh"),
            name_ja=r.get("name_ja"),
        )
        for r in raw
    )
