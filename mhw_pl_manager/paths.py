"""Resolve Monster Hunter: World install root (Steam registry + fallbacks)."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    import winreg
else:
    winreg = None  # type: ignore

STEAM_APP_ID = "582010"
CONFIG_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "mhw-pl-manager"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _read_config_root() -> Path | None:
    if not CONFIG_FILE.is_file():
        return None
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        root = data.get("game_root") or data.get("gameRoot")
        if root and Path(root).is_dir():
            return Path(root)
    except (json.JSONDecodeError, OSError):
        pass
    return None


def save_game_root(path: str | Path) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    p = Path(path)
    CONFIG_FILE.write_text(
        json.dumps({"game_root": str(p.resolve())}, indent=2),
        encoding="utf-8",
    )


def _uninstall_install_location() -> Path | None:
    if winreg is None:
        return None
    subkeys = [
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App {STEAM_APP_ID}"),
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App {STEAM_APP_ID}"),
    ]
    for hive, sk in subkeys:
        try:
            with winreg.OpenKey(hive, sk) as k:
                loc, _ = winreg.QueryValueEx(k, "InstallLocation")
                if loc:
                    p = Path(loc.strip('"'))
                    if p.is_dir():
                        return p
        except OSError:
            continue
    return None


def _steam_install_path() -> Path | None:
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"
        ) as k:
            raw, _ = winreg.QueryValueEx(k, "InstallPath")
            p = Path(raw.strip('"'))
            if p.is_dir():
                return p
    except OSError:
        pass
    return None


def _acf_installdir(acf_path: Path) -> str | None:
    try:
        text = acf_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r'"installdir"\s+"([^"]+)"', text)
    return m.group(1) if m else None


def _find_via_appmanifest(steam_root: Path) -> Path | None:
    manifest = steam_root / "steamapps" / f"appmanifest_{STEAM_APP_ID}.acf"
    if not manifest.is_file():
        return None
    installdir = _acf_installdir(manifest)
    if not installdir:
        return None
    game = steam_root / "steamapps" / "common" / installdir
    return game if game.is_dir() else None


def _library_paths_from_vdf(steam_root: Path) -> list[Path]:
    vdf = steam_root / "config" / "libraryfolders.vdf"
    if not vdf.is_file():
        return []
    try:
        text = vdf.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    paths: list[Path] = []
    for m in re.finditer(r'"path"\s+"([^"]+)"', text):
        raw = m.group(1).replace("\\\\", "\\")
        p = Path(raw)
        if p.is_dir():
            paths.append(p)
    return paths


def discover_game_root() -> Path | None:
    env = os.environ.get("MHW_ROOT")
    if env:
        p = Path(env.strip('"'))
        if p.is_dir():
            return p

    loc = _uninstall_install_location()
    if loc:
        return loc

    steam = _steam_install_path()
    if steam:
        game = _find_via_appmanifest(steam)
        if game:
            return game
        for lib in [steam, *_library_paths_from_vdf(steam)]:
            game = _find_via_appmanifest(lib)
            if game:
                return game
        guess = steam / "steamapps" / "common" / "Monster Hunter World"
        if guess.is_dir():
            return guess

    return None


def get_effective_game_root() -> Path | None:
    return _read_config_root() or discover_game_root()


def native_pc_root(game_root: Path) -> Path:
    return game_root / "nativePC"


def pl_f_equip(game_root: Path) -> Path:
    return native_pc_root(game_root) / "pl" / "f_equip"
