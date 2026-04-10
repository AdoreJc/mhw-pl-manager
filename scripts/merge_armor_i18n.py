"""
Merge MHWorldData armorset translations (ja / zh-TW) into data/armor_ids.json.

- Source CSV: data/armorset_name_translations.csv (from MHWorldData armorset_base_translations.csv)
- Chinese column is Traditional Chinese (in-game TW/HK)
- Optional per-id fixes: data/armor_i18n_overrides.json  { "123": { "name_ja": "...", "name_zh": "..." } }

Re-run after updating armor_ids.json:  python scripts/merge_armor_i18n.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARMOR_JSON = ROOT / "data" / "armor_ids.json"
TRANS_CSV = ROOT / "data" / "armorset_name_translations.csv"
OVERRIDES_JSON = ROOT / "data" / "armor_i18n_overrides.json"
EXTRAS_JSON = ROOT / "data" / "armor_name_locale_extras.json"

# Wiki / in-game UI short names -> armorset name_en in MHWorldData
ALIASES: dict[str, str] = {
    "Chain": "Chainmail",
    "Hunter": "Hunter's",
    "Anjanath": "Anja",
    "Bazelgeuse": "Bazel",
    "Great Girros": "Girros",
    "Jyuratodus": "Jyura",
    "Tzitzi-Ya-Ku": "Tzitzi",
    "Kulu-Ya-Ku": "Kulu",
    "Pukei-Pukei": "Pukei",
    "Tobi-Kadachi": "Kadachi",
    "Paolumu": "Lumu",
    "Radobaan": "Baan",
    "Kulve": "Kulve Taroth",
    "Xeno": "Xeno'jiiva",
    "Uragaan": "Uragaan",
    "Deviljho": "Deviljho",
    "Lavasioth": "Lavasioth",
    "Beotodus": "Beo",
    "Seething Bazel": "Seething Bazel",
    "Savage Jho": "Savage Jho",
    "Ruiner Nergi": "Ruiner Nergi",
    "Raging Brachy": "Raging Brachy",
    "Furious Rajang": "Furious Rajang",
    "Stygian Zin": "Stygian Zin",
    "Frostfang Barioth": "Frostfang Barioth",
    "Golden Lune": "Golden Lune",
    "Silver Sol": "Silver Sol",
    "Rath Soul": "Rath Soul",
    "Rath Heart": "Rath Heart",
    "Diablos Nero": "Diablos Nero",
    "Death Garon": "Death Garon",
    "Blackveil Hazak": "Blackveil Hazak",
    "Shrieking Legia": "Shrieking Legia",
    "Lumu Phantasm": "Lumu Phantasm",
    "Fulgur Anja": "Fulgur Anja",
    "Acidic Glavenus": "Acidic Glavenus",
    "Brute Tigrex": "Brute Tigrex",
    "Viper Kadachi": "Viper Kadachi",
    "Coral Pukei": "Coral Pukei",
    "Guild Palace": "Guild Palace",
    "Guildwork": "Guildwork",
    "Beetle": "Butterfly",
    "Queen Beetle": "Butterfly",
    "Azure Age": "Azure Starlord",
    "Azure Age+": "Azure Starlord",
    "Geralt of Rivia": "Geralt",
    "Strategist Spectacles": "Strategist",
    "Dragonking Eyepatch": "Dragonking",
    "Pulverizing Feather": "Pulverizing Feather",
    "Skull Mask": "Skull",
    "Skull Scarf": "Skull",
    "Drachen": "Drachen",
}


def _norm_apostrophe(s: str) -> list[str]:
    raw = s.strip()
    return list(
        dict.fromkeys(
            [raw, raw.replace("\u2019", "'"), raw.replace("'", "\u2019")]
        )
    )


def key_candidates(name: str) -> list[str]:
    """Keys to try against armorset CSV (order: LR αβγ, then IB α+β+γ+)."""
    raw = name.strip()
    n = ALIASES.get(raw, raw)
    if not n:
        return []
    out: list[str] = []
    seen: set[str] = set()

    def add(k: str) -> None:
        if k not in seen:
            seen.add(k)
            out.append(k)

    if n.endswith("+"):
        core = ALIASES.get(n[:-1].strip(), n[:-1].strip())
        variants_plus = _norm_apostrophe(core)
        for v in variants_plus:
            for suffix in (" α+", " β+", " γ+"):
                add(v + suffix)
        return out

    variants = _norm_apostrophe(n)
    for v in variants:
        for suffix in ("", " α", " β", " γ"):
            add(v + suffix)
    for v in variants:
        for suffix in (" α+", " β+", " γ+"):
            add(v + suffix)
    return out


def load_table(path: Path) -> dict[str, tuple[str | None, str | None]]:
    out: dict[str, tuple[str | None, str | None]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = (row.get("name_en") or "").strip()
            if not en:
                continue
            ja = (row.get("name_ja") or "").strip() or None
            zh = (row.get("name_zh") or "").strip() or None
            out[en] = (ja, zh)
    return out


def load_overrides() -> dict[str, dict[str, str | None]]:
    if not OVERRIDES_JSON.is_file():
        return {}
    data = json.loads(OVERRIDES_JSON.read_text(encoding="utf-8"))
    return {str(k): v for k, v in data.items()}


def load_extras() -> dict[str, dict[str, str | None]]:
    if not EXTRAS_JSON.is_file():
        return {}
    return json.loads(EXTRAS_JSON.read_text(encoding="utf-8"))


def main() -> None:
    if not ARMOR_JSON.is_file():
        print("Missing armor_ids.json", file=sys.stderr)
        sys.exit(1)
    if not TRANS_CSV.is_file():
        print("Missing armorset_name_translations.csv", file=sys.stderr)
        sys.exit(1)

    table = load_table(TRANS_CSV)
    overrides = load_overrides()
    extras = load_extras()
    rows = json.loads(ARMOR_JSON.read_text(encoding="utf-8"))
    missing = 0
    for row in rows:
        aid = str(row["id"])
        ja, zh = None, None
        if aid in overrides:
            o = overrides[aid]
            ja = o.get("name_ja") or ja
            zh = o.get("name_zh") or zh
        if ja is None and zh is None:
            ename = row.get("name") or ""
            for key in key_candidates(ename):
                if key in table:
                    ja, zh = table[key]
                    break
        if ja is None and zh is None:
            ename = row.get("name") or ""
            ex = extras.get(ename)
            if ex:
                ja = ex.get("name_ja") or ja
                zh = ex.get("name_zh") or zh
        name = row.get("name") or ""
        if name == "Unavailable" and ja is None and zh is None:
            ja, zh = "利用不可", "無法使用"
        row["name_ja"] = ja
        row["name_zh"] = zh
        if name and name != "Unavailable" and ja is None and zh is None:
            missing += 1

    ARMOR_JSON.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Updated {len(rows)} rows; {missing} without ja/zh (English only).")


if __name__ == "__main__":
    main()
