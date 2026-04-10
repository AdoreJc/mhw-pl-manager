"""Scan nativePC/pl/f_equip and copy-rename armor mod files."""
from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path

# Reserved under f_equip; not listed as a mod package.
BACKUP_SUBDIR = "backup"
_EXCLUDED_LIST_NAMES = frozenset({BACKUP_SUBDIR.casefold()})

SLOTS = ("arm", "body", "helm", "leg", "wst")

# f_arm021_0000.mod3, f_helm105_0000.tex.001.png, .ccl, .ctc, .mrl3, etc.
FILE_RE = {s: re.compile(rf"^f_{s}(\d{{3}})_(\d{{4}})(.*)$", re.I) for s in SLOTS}


def _files_in_slot_dir(slot_dir: Path) -> list[Path]:
    """
    List mod files under a slot folder: either directly in slot_dir, or one level down
    (e.g. arm/mod/f_arm021_0000.mod3).
    """
    out: list[Path] = []
    if not slot_dir.is_dir():
        return out
    for child in sorted(slot_dir.iterdir()):
        if child.is_file():
            out.append(child)
        elif child.is_dir():
            try:
                for f in sorted(child.iterdir()):
                    if f.is_file():
                        out.append(f)
            except OSError:
                continue
    return out


def parse_pl_model(model_path: str) -> tuple[str, str]:
    """pl021_0000 -> ('021', '0000')."""
    m = re.match(r"^pl(\d{3})_(\d{4})$", model_path.strip(), re.I)
    if not m:
        raise ValueError(f"Invalid model path: {model_path!r}")
    return m.group(1).lower(), m.group(2).lower()


def mod_folder_name_for_model(model_path: str) -> str:
    """Target equipment folder name under f_equip, e.g. pl029_0001."""
    num, var = parse_pl_model(model_path)
    return f"pl{num}_{var}"


def slot_prefix(slot: str, num: str, variant: str) -> str:
    return f"f_{slot}{num}_{variant}"


def list_mod_dirs(f_equip: Path) -> list[str]:
    if not f_equip.is_dir():
        return []
    return sorted(
        p.name
        for p in f_equip.iterdir()
        if p.is_dir()
        and not p.name.startswith(".")
        and p.name.casefold() not in _EXCLUDED_LIST_NAMES
    )


def extract_models_from_mod(mod_path: Path) -> set[str]:
    found: set[str] = set()
    for slot in SLOTS:
        d = mod_path / slot
        if not d.is_dir():
            continue
        rx = FILE_RE[slot]
        for f in _files_in_slot_dir(d):
            m = rx.match(f.name)
            if m:
                found.add(f"pl{m.group(1)}_{m.group(2)}")
    return found


def slot_coverage_for_model(mod_path: Path, num: str, variant: str) -> dict[str, bool]:
    cov = {s: False for s in SLOTS}
    for slot in SLOTS:
        pfx = slot_prefix(slot, num, variant)
        d = mod_path / slot
        if not d.is_dir():
            continue
        for f in _files_in_slot_dir(d):
            if f.name.lower().startswith(pfx.lower()):
                cov[slot] = True
                break
    return cov


def mod_covers_model(mod_path: Path, model_path: str) -> dict[str, bool]:
    num, var = parse_pl_model(model_path)
    return slot_coverage_for_model(mod_path, num, var)


def aggregate_coverage(
    f_equip: Path, model_path: str
) -> tuple[bool, dict[str, bool], list[str]]:
    """Returns (any_slot_covered, per_slot OR across mods, mod names that touch this model)."""
    num, var = parse_pl_model(model_path)
    per_slot = {s: False for s in SLOTS}
    mods_hit: list[str] = []
    for name in list_mod_dirs(f_equip):
        mp = f_equip / name
        cov = slot_coverage_for_model(mp, num, var)
        if any(cov.values()):
            mods_hit.append(name)
        for s in SLOTS:
            per_slot[s] = per_slot[s] or cov[s]
    return any(per_slot.values()), per_slot, mods_hit


def copy_rename_between_models(
    source_mod: Path,
    target_mod: Path,
    source_model: str,
    target_model: str,
) -> list[str]:
    """
    Copy files from source_mod slot folders into target_mod, renaming pl id segment.
    Returns list of created relative paths (posix).
    """
    sn, sv = parse_pl_model(source_model)
    tn, tv = parse_pl_model(target_model)
    created: list[str] = []
    if sn == tn and sv == tv:
        try:
            if source_mod.resolve() == target_mod.resolve():
                return []
        except OSError:
            pass
    target_mod.mkdir(parents=True, exist_ok=True)

    for slot in SLOTS:
        src_dir = source_mod / slot
        if not src_dir.is_dir():
            continue
        old_pfx = slot_prefix(slot, sn, sv)
        new_pfx = slot_prefix(slot, tn, tv)
        dst_root = target_mod / slot
        dst_root.mkdir(parents=True, exist_ok=True)

        for child in sorted(src_dir.iterdir()):
            if child.is_file():
                candidates = [child]
                rel_sub = ""
            elif child.is_dir():
                try:
                    candidates = sorted(
                        p for p in child.iterdir() if p.is_file()
                    )
                except OSError:
                    continue
                rel_sub = child.name
            else:
                continue

            for f in candidates:
                m = re.match(re.escape(old_pfx) + r"(.*)$", f.name, re.I)
                if not m:
                    continue
                new_name = f"{new_pfx}{m.group(1)}"
                if rel_sub:
                    dest_dir = dst_root / rel_sub
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / new_name
                    rel = f"{target_mod.name}/{slot}/{rel_sub}/{new_name}"
                else:
                    dest = dst_root / new_name
                    rel = f"{target_mod.name}/{slot}/{new_name}"
                shutil.copy2(f, dest)
                created.append(rel)
    return created


def backup_mod_folder(mod_path: Path, backup_parent: Path) -> Path:
    """
    Copy the entire mod folder into backup_parent with a timestamp suffix.
    backup_parent is typically nativePC/pl/f_equip/backup.
    """
    backup_parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = mod_path.name
    dest = backup_parent / f"{base}_{stamp}"
    n = 0
    while dest.exists():
        n += 1
        dest = backup_parent / f"{base}_{stamp}_{n}"
    shutil.copytree(mod_path, dest)
    return dest
