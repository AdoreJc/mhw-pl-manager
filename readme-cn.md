<!-- 语言：简体中文 -->

## MHW f_equip Mod 管理器

这是一个基于 **FastAPI** 的本地网页工具，用来管理怪物猎人世界（MHW）`nativePC/pl/f_equip` 下的装备换肤/套用类 Mod。

它可以列出已安装的 `f_equip` Mod、查看各个装备 model 的覆盖情况，并支持把一个 `plXXX_YYYY` 的皮肤 **复制并改名** 套用到另一个目标 `plXXX_YYYY`。同时也支持直接拖拽导入压缩包（`.zip` / `.7z` / `.rar`），自动识别压缩包内的 `plXXX_YYYY` 目录后套用。

## 功能

- **设置游戏目录**：通过界面手动设置，或使用 `MHW_ROOT` 环境变量（目录需包含 `nativePC`）。
- **Mod 列表**：列出 `nativePC/pl/f_equip/*` 的 Mod 文件夹，并检测包含的 model。
- **装备覆盖**：按部位（slot）展示某个装备 model 是否已有 Mod 覆盖，以及来自哪些 Mod。
- **套用（已安装 Mod）**：从已安装 Mod 中选择源 model，复制并改名到目标 model。
- **套用（压缩包导入）**：拖拽 `.zip/.7z/.rar`，自动识别 `plXXX_YYYY`，选择源后套用到目标。
- **可选备份**：覆盖前把目标目录备份到 `f_equip/backup`。

## 环境要求

- Python 3.10+（推荐）
- 依赖见 `requirements.txt`

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python -m mhw_pl_manager
```

然后在浏览器打开：

- `http://127.0.0.1:8765/`

## 设置游戏根目录

必须先设置 MHW 游戏根目录（也就是包含 `nativePC` 的那个目录）：

- **界面中**：点击“手动设置”选择/输入路径。
- **环境变量**：设置 `MHW_ROOT` 为游戏根目录路径。

## 注意事项

- 本工具会直接在 `nativePC/pl/f_equip` 下**写入/覆盖文件**。建议勾选备份，方便回滚。
- 压缩包导入支持 `.zip`、`.7z`、`.rar`。某些 `.rar` 可能需要系统已安装 UnRAR 等外部工具才能解包。

