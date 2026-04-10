"""Inspect and extract MHW archives that contain plXXX_YYYY source folders."""
from __future__ import annotations

import re
import tempfile
import uuid
import zipfile
from pathlib import Path
from time import time
from mhw_pl_manager import f_equip as fe

PL_DIR_RE = re.compile(r"^pl(\d{3})_(\d{4})$", re.I)

_SESSIONS: dict[str, dict] = {}
SESSION_TTL_SEC = 3600


def _cleanup_sessions() -> None:
    now = time()
    dead = [sid for sid, s in _SESSIONS.items() if now - s["created"] > SESSION_TTL_SEC]
    for sid in dead:
        _drop_session(sid)


def _drop_session(sid: str) -> None:
    s = _SESSIONS.pop(sid, None)
    if not s:
        return
    p = s.get("path")
    if p and Path(p).is_file():
        try:
            Path(p).unlink()
        except OSError:
            pass


def register_session(archive_path: Path) -> str:
    _cleanup_sessions()
    sid = uuid.uuid4().hex
    _SESSIONS[sid] = {"path": str(archive_path.resolve()), "created": time()}
    return sid


def get_session_path(sid: str) -> Path | None:
    _cleanup_sessions()
    s = _SESSIONS.get(sid)
    if not s:
        return None
    p = Path(s["path"])
    return p if p.is_file() else None


def consume_session(sid: str) -> Path | None:
    p = get_session_path(sid)
    if p:
        _SESSIONS.pop(sid, None)
    return p


def _norm_arc_path(p: str) -> str:
    return p.replace("\\", "/").lstrip("./")


def list_zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path, "r") as zf:
        return [_norm_arc_path(n) for n in zf.namelist()]


def list_7z_names(path: Path) -> list[str]:
    import py7zr

    with py7zr.SevenZipFile(path, mode="r") as z:
        return [_norm_arc_path(n) for n in z.getnames()]


def list_rar_names(path: Path) -> list[str]:
    import rarfile

    with rarfile.RarFile(path) as rf:
        return [_norm_arc_path(n) for n in rf.namelist()]


def list_archive_member_names(path: Path) -> list[str]:
    suf = path.suffix.lower()
    if suf == ".zip":
        return list_zip_names(path)
    if suf == ".7z":
        return list_7z_names(path)
    if suf == ".rar":
        return list_rar_names(path)
    raise ValueError(f"不支持的压缩格式: {suf}（请使用 .zip / .7z / .rar）")


def _classify_priority(parts: list[str], idx: int) -> int:
    # Prefer canonical layout .../nativePC/pl/f_equip/plXXX_YYYY
    p3 = parts[idx - 3].lower() if idx >= 3 else ""
    p2 = parts[idx - 2].lower() if idx >= 2 else ""
    p1 = parts[idx - 1].lower() if idx >= 1 else ""
    if p3 == "nativepc" and p2 == "pl" and p1 == "f_equip":
        return 0
    if p2 == "pl" and p1 == "f_equip":
        return 1
    # mod_hepsy is optional now, but still a useful hint
    if p1 == "mod_hepsy":
        return 2
    return 10


def find_pl_sources(names: list[str]) -> dict[str, str]:
    """
    Find source folders for each pl model in archive entries.
    Returns mapping: plXXX_YYYY -> archive-relative folder path ending at that pl dir.
    """
    best: dict[str, tuple[int, str]] = {}
    for raw in names:
        norm = _norm_arc_path(raw)
        if not norm:
            continue
        parts = [x for x in norm.split("/") if x]
        for i, part in enumerate(parts):
            m = PL_DIR_RE.match(part)
            if not m:
                continue
            pl = f"pl{m.group(1)}_{m.group(2)}".lower()
            pref = "/".join(parts[: i + 1])
            prio = _classify_priority(parts, i)
            prev = best.get(pl)
            if prev is None or prio < prev[0]:
                best[pl] = (prio, pref)
    return {pl: pref for pl, (_, pref) in best.items()}


def _safe_extract_zip(zf: zipfile.ZipFile, dest: Path) -> None:
    dest = dest.resolve()
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        if name.startswith("/") or ".." in name.split("/"):
            raise ValueError("压缩包路径不安全")
        target = (dest / name).resolve()
        if dest not in target.parents and target != dest:
            raise ValueError("压缩包路径不安全")
    zf.extractall(dest)


def extract_archive(archive_path: Path, dest: Path) -> None:
    suf = archive_path.suffix.lower()
    dest.mkdir(parents=True, exist_ok=True)
    if suf == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zf:
            _safe_extract_zip(zf, dest)
        return
    if suf == ".7z":
        import py7zr

        with py7zr.SevenZipFile(archive_path, mode="r") as z:
            z.extractall(path=dest)
        return
    if suf == ".rar":
        import rarfile

        with rarfile.RarFile(archive_path) as rf:
            rf.extractall(path=dest)
        return
    raise ValueError(f"不支持的压缩格式: {suf}")


def resolve_source_on_disk(extract_root: Path, source_prefix: str) -> Path:
    """source_prefix is archive-relative path that ends at plXXX_YYYY folder."""
    rel = Path(source_prefix.replace("\\", "/"))
    candidate = (extract_root / rel).resolve()
    er = extract_root.resolve()
    if er not in candidate.parents and candidate != er:
        raise ValueError("解压路径异常")
    if not candidate.is_dir():
        raise ValueError("解压后未找到所选 pl 源目录")
    return candidate


def target_folder_nonempty(f_equip: Path, target_model: str) -> bool:
    name = fe.mod_folder_name_for_model(target_model)
    p = f_equip / name
    if not p.is_dir():
        return False
    try:
        next(p.iterdir())
    except StopIteration:
        return False
    return True


def apply_mod_hepsy_archive(
    archive_path: Path,
    f_equip: Path,
    target_model: str,
    source_pl: str,
    *,
    backup_existing: bool,
    overwrite: bool,
    source_prefix: str,
) -> tuple[list[str], str | None, str]:
    """
    Extract archive to temp, copy-rename from selected pl source folder to target folder.
    Returns (created_rel_paths, backup_path or None, target_folder_name).
    """
    fe.parse_pl_model(target_model)
    fe.parse_pl_model(source_pl)
    target_name = fe.mod_folder_name_for_model(target_model)
    tgt = f_equip / target_name

    nonempty = target_folder_nonempty(f_equip, target_model)
    if nonempty and not overwrite:
        raise ValueError("目标装备目录已存在文件，需要确认覆盖后再安装")

    with tempfile.TemporaryDirectory(prefix="mhw_mod_hepsy_") as td:
        root = Path(td)
        extract_archive(archive_path, root)
        src_mod = resolve_source_on_disk(root, source_prefix)

        backup_path: str | None = None
        if nonempty and overwrite and backup_existing:
            backup_root = f_equip / fe.BACKUP_SUBDIR
            dest_bak = fe.backup_mod_folder(tgt, backup_root)
            backup_path = str(dest_bak)

        created = fe.copy_rename_between_models(src_mod, tgt, source_pl, target_model)
        if not created:
            raise ValueError(
                "未复制任何文件：请确认源目录的 arm/body/helm/leg/wst 下存在与所选 model 匹配的文件。"
            )
        return created, backup_path, target_name
