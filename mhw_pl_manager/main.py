"""FastAPI app: MHW pl f_equip mod manager."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mhw_pl_manager import __version__
from mhw_pl_manager import f_equip as fe
from mhw_pl_manager.archive_mod_hepsy import (
    apply_mod_hepsy_archive,
    consume_session,
    find_pl_sources,
    list_archive_member_names,
    register_session,
    target_folder_nonempty,
)
from mhw_pl_manager.armor_catalog import load_armor_entries
from mhw_pl_manager.paths import (
    get_effective_game_root,
    native_pc_root,
    pl_f_equip,
    save_game_root,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"

app = FastAPI(title="MHW PL Mod Manager", version=__version__)


class SetGameRootBody(BaseModel):
    path: str = Field(..., description="Monster Hunter World root (folder containing nativePC)")


class ApplyModBody(BaseModel):
    source_mod: str = Field(..., description="f_equip subfolder to copy from")
    source_model: str = Field(..., description="Wiki model path e.g. pl021_0000")
    target_model: str = Field(..., description="Target model path e.g. pl033_0000")
    backup_existing: bool = Field(
        False,
        description="If target folder plXXX_YYYY exists, copy it to f_equip/backup first",
    )


class ArchiveModHepApplyBody(BaseModel):
    session_id: str = Field(..., description="From /api/archive-mod-hepsy/inspect")
    source_pl: str = Field(..., description="Selected source model folder name, e.g. pl021_0000")
    target_model: str = Field(..., description="Target equipment model e.g. pl033_0000")
    backup_existing: bool = Field(False, description="Backup target folder before overwrite")
    overwrite: bool = Field(False, description="Replace existing target mod files")
    source_prefix: str = Field(..., description="Archive-relative path ending with source pl dir")


class RemoveModBody(BaseModel):
    target_model: str = Field(..., description="Target equipment model e.g. pl033_0000")
    backup_before_remove: bool = Field(False, description="Backup target folder before delete")


def _game_or_404():
    root = get_effective_game_root()
    if not root:
        raise HTTPException(
            status_code=400,
            detail="未找到游戏目录。请设置 Steam 版安装路径或设置 MHW_ROOT 环境变量。",
        )
    return root


def _armor_names(e) -> dict:
    return {"name": e.name, "name_zh": e.name_zh, "name_ja": e.name_ja}


def _layout(root: Path) -> dict:
    npc = native_pc_root(root) / "npc"
    pl = native_pc_root(root) / "pl"
    f_eq = pl / "f_equip"
    return {
        "game_root": str(root),
        "native_pc": str(native_pc_root(root)),
        "has_native_pc": native_pc_root(root).is_dir(),
        "has_npc": npc.is_dir(),
        "has_pl": pl.is_dir(),
        "has_f_equip": f_eq.is_dir(),
        "f_equip": str(f_eq),
    }


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/game")
def get_game():
    root = get_effective_game_root()
    if not root:
        return {
            "game_root": None,
            "error": "not_found",
            "has_native_pc": False,
            "has_npc": False,
            "has_pl": False,
            "has_f_equip": False,
        }
    return _layout(root)


@app.post("/api/game")
def post_game(body: SetGameRootBody):
    p = Path(body.path)
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="路径不存在或不是目录")
    if not (p / "nativePC").is_dir():
        raise HTTPException(
            status_code=400,
            detail="该目录下没有 nativePC，请确认是怪物猎人世界游戏根目录。",
        )
    save_game_root(p)
    return _layout(p)


@app.get("/api/mods")
def list_mods():
    root = _game_or_404()
    f_eq = pl_f_equip(root)
    if not f_eq.is_dir():
        raise HTTPException(status_code=400, detail="未找到 nativePC/pl/f_equip 目录")
    out = []
    for name in fe.list_mod_dirs(f_eq):
        mp = f_eq / name
        models = sorted(fe.extract_models_from_mod(mp))
        out.append({"name": name, "models": models, "path": str(mp)})
    return {"mods": out, **_layout(root)}


@app.get("/api/armor/coverage")
def armor_coverage():
    root = _game_or_404()
    f_eq = pl_f_equip(root)
    entries = load_armor_entries()
    rows = []
    for e in entries:
        if not e.model_path:
            rows.append(
                {
                    "id": e.id,
                    **_armor_names(e),
                    "model_path": None,
                    "has_mod": False,
                    "slots": {s: False for s in fe.SLOTS},
                    "mods": [],
                    "skipped": True,
                }
            )
            continue
        if not f_eq.is_dir():
            rows.append(
                {
                    "id": e.id,
                    **_armor_names(e),
                    "model_path": e.model_path,
                    "has_mod": False,
                    "slots": {s: False for s in fe.SLOTS},
                    "mods": [],
                    "skipped": False,
                }
            )
            continue
        try:
            any_cov, slots, mods = fe.aggregate_coverage(f_eq, e.model_path)
        except ValueError:
            rows.append(
                {
                    "id": e.id,
                    **_armor_names(e),
                    "model_path": e.model_path,
                    "has_mod": False,
                    "slots": {s: False for s in fe.SLOTS},
                    "mods": [],
                    "skipped": True,
                    "note": "invalid_model_path",
                }
            )
            continue
        rows.append(
            {
                "id": e.id,
                **_armor_names(e),
                "model_path": e.model_path,
                "has_mod": any_cov,
                "slots": slots,
                "mods": mods,
                "skipped": False,
            }
        )
    return {"armor": rows, **_layout(root)}


@app.post("/api/apply-mod")
def apply_mod(body: ApplyModBody):
    root = _game_or_404()
    f_eq = pl_f_equip(root)
    if not f_eq.is_dir():
        raise HTTPException(status_code=400, detail="未找到 nativePC/pl/f_equip")
    src = f_eq / body.source_mod
    if not src.is_dir():
        raise HTTPException(status_code=400, detail=f"源 Mod 不存在: {body.source_mod}")
    try:
        fe.parse_pl_model(body.source_model)
        fe.parse_pl_model(body.target_model)
        target_name = fe.mod_folder_name_for_model(body.target_model)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    tgt = f_eq / target_name
    backup_path = None
    if body.backup_existing and tgt.is_dir():
        backup_root = f_eq / fe.BACKUP_SUBDIR
        backup_path = fe.backup_mod_folder(tgt, backup_root)
    created = fe.copy_rename_between_models(src, tgt, body.source_model, body.target_model)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="未复制任何文件：请确认源 Mod 的 arm/body/helm/leg/wst 下存在与 source_model 匹配的文件名。",
        )
    out: dict = {
        "ok": True,
        "files_created": created,
        "count": len(created),
        "target_folder": target_name,
    }
    if backup_path is not None:
        out["backup_path"] = str(backup_path)
    return out


_ALLOWED_ARCHIVE_EXT = {".zip", ".7z", ".rar"}


@app.post("/api/archive-mod-hepsy/inspect")
async def archive_mod_hepsy_inspect(
    file: UploadFile = File(...),
    target_model: str = Form(""),
):
    """Upload zip/7z/rar; find source pl folders from archive."""
    root = _game_or_404()
    raw_name = file.filename or "mod.zip"
    suffix = Path(raw_name).suffix.lower()
    if suffix not in _ALLOWED_ARCHIVE_EXT:
        raise HTTPException(
            status_code=400,
            detail="仅支持 .zip、.7z、.rar",
        )
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
    except OSError as err:
        raise HTTPException(status_code=400, detail=f"无法保存上传文件: {err}") from err

    def fail(msg: str):
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=msg)

    try:
        names = list_archive_member_names(tmp_path)
    except Exception as err:  # noqa: BLE001
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=f"无法读取压缩包（若为 .rar 请安装 UnRAR 或改用 zip/7z）: {err}",
        ) from err

    pl_sources = find_pl_sources(names)
    candidates = sorted(pl_sources.keys())
    if not candidates:
        fail("压缩包内未找到 plXXX_YYYY 类型目录")

    target_has = False
    tm = target_model.strip()
    if tm:
        try:
            fe.parse_pl_model(tm)
        except ValueError:
            tm = ""
        if tm:
            f_eq = pl_f_equip(root)
            if f_eq.is_dir():
                target_has = target_folder_nonempty(f_eq, tm)

    session_id = register_session(tmp_path)
    return {
        "ok": True,
        "session_id": session_id,
        "pl_candidates": candidates,
        "pl_sources": pl_sources,
        "target_has_files": target_has,
    }


@app.post("/api/archive-mod-hepsy/apply")
def archive_mod_hepsy_apply(body: ArchiveModHepApplyBody):
    root = _game_or_404()
    f_eq = pl_f_equip(root)
    if not f_eq.is_dir():
        raise HTTPException(status_code=400, detail="未找到 nativePC/pl/f_equip")

    path = consume_session(body.session_id)
    if not path or not path.is_file():
        raise HTTPException(status_code=400, detail="导入会话已失效，请重新拖拽压缩包")

    try:
        created, backup_path, target_name = apply_mod_hepsy_archive(
            path,
            f_eq,
            body.target_model,
            body.source_pl,
            backup_existing=body.backup_existing,
            overwrite=body.overwrite,
            source_prefix=body.source_prefix,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    finally:
        path.unlink(missing_ok=True)

    out: dict = {
        "ok": True,
        "files_created": created,
        "count": len(created),
        "target_folder": target_name,
    }
    if backup_path is not None:
        out["backup_path"] = backup_path
    return out


@app.post("/api/remove-mod")
def remove_mod(body: RemoveModBody):
    root = _game_or_404()
    f_eq = pl_f_equip(root)
    if not f_eq.is_dir():
        raise HTTPException(status_code=400, detail="未找到 nativePC/pl/f_equip")
    try:
        fe.parse_pl_model(body.target_model)
        target_name = fe.mod_folder_name_for_model(body.target_model)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    tgt = f_eq / target_name
    if not tgt.is_dir():
        raise HTTPException(status_code=400, detail="目标目录不存在，无需移除")

    backup_path = None
    if body.backup_before_remove:
        backup_root = f_eq / fe.BACKUP_SUBDIR
        backup_path = fe.backup_mod_folder(tgt, backup_root)

    try:
        shutil.rmtree(tgt)
    except OSError as err:
        raise HTTPException(status_code=400, detail=f"移除失败: {err}") from err

    out: dict = {"ok": True, "removed_folder": target_name}
    if backup_path is not None:
        out["backup_path"] = str(backup_path)
    return out


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    index_html = STATIC_DIR / "index.html"
    if not index_html.is_file():
        raise HTTPException(status_code=404, detail="前端未安装")
    return FileResponse(index_html)
