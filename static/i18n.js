/**
 * UI strings: English, Simplified / Traditional Chinese UI, Japanese.
 * Armor row names come from API (name / name_zh / name_ja); name_zh is in-game Traditional (TW/HK).
 */
const UI = {
  en: {
    uiLang: "UI language",
    pageTitle: "MHW f_equip Mod Manager (female)",
    heading: "MHW f_equip Mod Manager",
    subHtml:
      'Reads <code>nativePC/pl/f_equip</code> subfolders (each is a mod), matches <a href="https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Armor-IDs" target="_blank" rel="noopener">Armor IDs</a>; copy-rename skins to other equipment IDs.',
    langNote: "Armor 中文 uses in-game Traditional Chinese (TW/HK) from MHWorldData.",
    gameDir: "Game folder",
    pathPlaceholder: "Detecting…",
    manualPath: "Set manually",
    tabArmor: "Armor list",
    tabMods: "Mod list",
    filterAll: "All",
    filterMissing: "No mod",
    filterCovered: "Has mod",
    armorFilterGroup: "Filter armor list",
    filterPlaceholder: "Filter by name, armor ID, or model pl-XXX (e.g. 029)…",
    thId: "ID",
    thName: "Armor",
    thModel: "Model",
    thSlots: "Slots",
    thAction: "Action",
    thMods: "Mods",
    btnApply: "Apply mod…",
    modListHint:
      "Each subfolder should have arm/body/helm/leg/wst; files may sit one level deeper (e.g. arm/mod/f_arm021_0000.mod3). Filenames matching f_<slot> + 3 digits + _ + 4 digits are detected.",
    dlgTitle: "Copy skin to this armor",
    dlgDropHint: "Drop .zip / .7z / .rar (auto-detects plXXX_YYYY folders)",
    dlgArchiveSourcePl: "Source model inside the archive (under mod_hepsy)",
    dlgClearArchive: "Use installed mod instead",
    dlgSourceMod: "Source mod folder",
    dlgSourceModel: "Source model (pl path in that mod)",
    dlgOutputFolder: (pl) => `Output folder: nativePC/pl/f_equip/${pl}`,
    dlgBackup: "Back up existing folder to nativePC/pl/f_equip/backup before overwrite",
    dlgWarn: "Files are copied and renamed into that folder; same names are overwritten.",
    dlgSubmit: "Copy & rename",
    dlgCancel: "Cancel",
    dlgRemoveTitle: "Remove this armor mod",
    dlgRemoveWarn: "This deletes the corresponding f_equip/plXXX_YYYY folder.",
    dlgRemoveBackup: "Back up & remove",
    dlgRemoveNoBackup: "Remove without backup",
    btnRemove: "Remove",
    flagYes: "yes",
    flagNo: "no",
    gameMissing: "Game path not found. Click “Set manually”.",
    toastSavedPath: "Game path saved.",
    toastWrote: (n) => `Wrote ${n} file(s).`,
    toastBackedUp: (p) => `Backed up to: ${p}`,
    toastPickModel: "Pick a valid source model.",
    slot: { helm: "helm", body: "body", arm: "arm", leg: "leg", wst: "wst" },
    countSuffix: "entries",
    thModFolder: "Mod folder",
    thModelsDetected: "Models found",
    promptGamePath: "Path to Monster Hunter: World root (folder containing nativePC):",
    noModsFound: "No mod folders found.",
    noModsOrArchive: "Install a mod under f_equip, or drop an archive that contains mod_hepsy.",
    confirmOverwriteArchive:
      "Target armor folder already has files. Overwrite with this import?",
    toastArchiveLoaded: "Archive loaded; pick source model and apply.",
    toastBadArchiveType: "Only .zip, .7z, and .rar are supported.",
    errRequest: "Request failed",
    emptyParsedMod: "(No f_* files parsed in this mod)",
  },
  "zh-Hans": {
    uiLang: "界面语言",
    pageTitle: "MHW f_equip Mod 管理器",
    heading: "MHW f_equip Mod 管理器",
    subHtml:
      '读取 <code>nativePC/pl/f_equip</code> 下各子文件夹（每个即一个 Mod），对照 <a href="https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Armor-IDs" target="_blank" rel="noopener">Armor IDs</a>；可将皮肤复制并重命名为其他装备 ID。',
    langNote: "装备中文为游戏内繁体（MHWorldData，台港澳版本）。简体界面下装备名仍显示该套官方文本。",
    gameDir: "游戏目录",
    pathPlaceholder: "自动检测中…",
    manualPath: "手动设置",
    tabArmor: "装备列表",
    tabMods: "Mod 列表",
    filterAll: "全部",
    filterMissing: "无 Mod",
    filterCovered: "已有 Mod",
    armorFilterGroup: "筛选装备列表",
    filterPlaceholder: "按名称、装备 ID、或 Model 三位 pl ID（如 029）筛选…",
    thId: "ID",
    thName: "装备名",
    thModel: "Model",
    thSlots: "部位覆盖",
    thAction: "操作",
    thMods: "所在 Mod",
    btnApply: "套用已有 Mod…",
    modListHint:
      "子文件夹内应有 arm / body / helm / leg / wst；模型可在部位下再套一层子目录（例如 arm/mod/f_arm021_0000.mod3）。凡文件名以 f_部位 + 三位 + _ + 四位开头均会识别。",
    dlgTitle: "套用皮肤到当前装备",
    dlgDropHint: "拖拽 .zip / .7z / .rar（自动识别 plXXX_YYYY 目录）",
    dlgArchiveSourcePl: "压缩包内的源 model（mod_hepsy 下）",
    dlgClearArchive: "改用已安装的 Mod",
    dlgSourceMod: "源 Mod 文件夹",
    dlgSourceModel: "源 model（该 Mod 中的 pl 路径）",
    dlgOutputFolder: (pl) => `输出目录：nativePC/pl/f_equip/${pl}（依装备 ID 自动命名）`,
    dlgBackup: "若该目录已存在，先整夹备份到 f_equip/backup 再覆盖",
    dlgWarn: "文件将复制并重命名到上述目录；同名文件会被覆盖。",
    dlgSubmit: "复制并改名",
    dlgCancel: "取消",
    dlgRemoveTitle: "移除该装备 Mod",
    dlgRemoveWarn: "将删除该装备对应的 f_equip/plXXX_YYYY 目录。",
    dlgRemoveBackup: "备份并移除",
    dlgRemoveNoBackup: "不备份并移除",
    btnRemove: "移除",
    flagYes: "有",
    flagNo: "无",
    gameMissing: "未检测到游戏目录，请点击「手动设置」。",
    toastSavedPath: "已保存游戏路径。",
    toastWrote: (n) => `已写入 ${n} 个文件。`,
    toastBackedUp: (p) => `已备份至：${p}`,
    toastPickModel: "请选择有效的源 model。",
    slot: { helm: "头", body: "身", arm: "手", leg: "腿", wst: "腰" },
    countSuffix: "条",
    thModFolder: "Mod 文件夹",
    thModelsDetected: "检测到的 model",
    promptGamePath: "请输入怪物猎人世界游戏根目录（包含 nativePC 的文件夹）:",
    noModsFound: "没有检测到任何 Mod 文件夹。",
    noModsOrArchive: "请在 f_equip 下安装 Mod，或拖拽包含 mod_hepsy 的压缩包。",
    confirmOverwriteArchive: "目标装备目录已有文件，是否覆盖安装？",
    toastArchiveLoaded: "已载入压缩包，请选择源 model 后套用。",
    toastBadArchiveType: "仅支持 .zip、.7z、.rar。",
    errRequest: "请求失败",
    emptyParsedMod: "（该 Mod 未解析到标准 f_* 文件）",
  },
  "zh-Hant": {
    uiLang: "介面語言",
    pageTitle: "MHW f_equip Mod 管理器",
    heading: "MHW f_equip Mod 管理器",
    subHtml:
      '讀取 <code>nativePC/pl/f_equip</code> 下各子資料夾（每個即一個 Mod），對照 <a href="https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Armor-IDs" target="_blank" rel="noopener">Armor IDs</a>；可將外觀複製並重新命名為其他裝備 ID。',
    langNote: "裝備中文為遊戲內繁體（MHWorldData 官方文本，台港用語）。",
    gameDir: "遊戲目錄",
    pathPlaceholder: "自動偵測中…",
    manualPath: "手動設定",
    tabArmor: "裝備列表",
    tabMods: "Mod 列表",
    filterAll: "全部",
    filterMissing: "無 Mod",
    filterCovered: "已有 Mod",
    armorFilterGroup: "篩選裝備列表",
    filterPlaceholder: "依名稱、裝備 ID、或 Model 三位 pl ID（如 029）篩選…",
    thId: "ID",
    thName: "裝備名",
    thModel: "Model",
    thSlots: "部位覆蓋",
    thAction: "操作",
    thMods: "所在 Mod",
    btnApply: "套用已有 Mod…",
    modListHint:
      "子資料夾內應有 arm / body / helm / leg / wst；模型可在部位下再套一層子目錄（例如 arm/mod/f_arm021_0000.mod3）。凡檔名以 f_部位 + 三位 + _ + 四位開頭均會辨識。",
    dlgTitle: "套用外觀到目前裝備",
    dlgDropHint: "拖曳 .zip / .7z / .rar（自動辨識 plXXX_YYYY 目錄）",
    dlgArchiveSourcePl: "壓縮檔內的來源 model（mod_hepsy 下）",
    dlgClearArchive: "改用已安裝的 Mod",
    dlgSourceMod: "來源 Mod 資料夾",
    dlgSourceModel: "來源 model（該 Mod 中的 pl 路徑）",
    dlgOutputFolder: (pl) => `輸出目錄：nativePC/pl/f_equip/${pl}（依裝備 ID 自動命名）`,
    dlgBackup: "若該目錄已存在，先整夾備份到 f_equip/backup 再覆寫",
    dlgWarn: "檔案將複製並重新命名到上述目錄；同名檔案會被覆寫。",
    dlgSubmit: "複製並改名",
    dlgCancel: "取消",
    dlgRemoveTitle: "移除該裝備 Mod",
    dlgRemoveWarn: "將刪除此裝備對應的 f_equip/plXXX_YYYY 目錄。",
    dlgRemoveBackup: "備份並移除",
    dlgRemoveNoBackup: "不備份並移除",
    btnRemove: "移除",
    flagYes: "有",
    flagNo: "無",
    gameMissing: "未偵測到遊戲目錄，請點選「手動設定」。",
    toastSavedPath: "已儲存遊戲路徑。",
    toastWrote: (n) => `已寫入 ${n} 個檔案。`,
    toastBackedUp: (p) => `已備份至：${p}`,
    toastPickModel: "請選擇有效的來源 model。",
    slot: { helm: "頭", body: "身", arm: "手", leg: "腿", wst: "腰" },
    countSuffix: "筆",
    thModFolder: "Mod 資料夾",
    thModelsDetected: "偵測到的 model",
    promptGamePath: "請輸入魔物獵人 世界遊戲根目錄（包含 nativePC 的資料夾）:",
    noModsFound: "沒有偵測到任何 Mod 資料夾。",
    noModsOrArchive: "請在 f_equip 下安裝 Mod，或拖曳含 mod_hepsy 的壓縮檔。",
    confirmOverwriteArchive: "目標裝備目錄已有檔案，是否覆蓋安裝？",
    toastArchiveLoaded: "已載入壓縮檔，請選擇來源 model 後套用。",
    toastBadArchiveType: "僅支援 .zip、.7z、.rar。",
    errRequest: "請求失敗",
    emptyParsedMod: "（此 Mod 未解析到標準 f_* 檔案）",
  },
  ja: {
    uiLang: "表示言語",
    pageTitle: "MHW f_equip Mod 管理",
    heading: "MHW f_equip Mod 管理",
    subHtml:
      '<code>nativePC/pl/f_equip</code> 内の各サブフォルダ（1 Mod）を読み取り、<a href="https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Armor-IDs" target="_blank" rel="noopener">Armor IDs</a> と対応。他装備 ID へコピー＆リネーム可能。',
    langNote: "装備名の日本語はゲーム公式訳（MHWorldData）です。",
    gameDir: "ゲームフォルダ",
    pathPlaceholder: "検索中…",
    manualPath: "手動で指定",
    tabArmor: "装備一覧",
    tabMods: "Mod 一覧",
    filterAll: "すべて",
    filterMissing: "Mod なし",
    filterCovered: "Mod あり",
    armorFilterGroup: "装備リストの絞り込み",
    filterPlaceholder: "名前・装備 ID・model の pl 先頭3桁（例 029）で絞り込み…",
    thId: "ID",
    thName: "装備名",
    thModel: "Model",
    thSlots: "部位",
    thAction: "操作",
    thMods: "Mod フォルダ",
    btnApply: "Mod を適用…",
    modListHint:
      "各サブフォルダに arm/body/helm/leg/wst。arm/mod/ のように一段ネストした先の f_arm021_0000.* も認識します。",
    dlgTitle: "この装備にスキンを適用",
    dlgDropHint: ".zip / .7z / .rar をドロップ（plXXX_YYYY フォルダを自動検出）",
    dlgArchiveSourcePl: "アーカイブ内の元 model（mod_hepsy 配下）",
    dlgClearArchive: "インストール済み Mod を使う",
    dlgSourceMod: "コピー元 Mod フォルダ",
    dlgSourceModel: "元 model（その Mod 内の pl）",
    dlgOutputFolder: (pl) => `出力: nativePC/pl/f_equip/${pl}（装備 ID から自動）`,
    dlgBackup: "既存フォルダがある場合、上書き前に f_equip/backup へ丸ごとコピー",
    dlgWarn: "上記フォルダへコピー＆リネームします。同名は上書きされます。",
    dlgSubmit: "コピーしてリネーム",
    dlgCancel: "キャンセル",
    dlgRemoveTitle: "この装備の Mod を削除",
    dlgRemoveWarn: "対応する f_equip/plXXX_YYYY フォルダを削除します。",
    dlgRemoveBackup: "バックアップして削除",
    dlgRemoveNoBackup: "バックアップせず削除",
    btnRemove: "削除",
    flagYes: "あり",
    flagNo: "なし",
    gameMissing: "ゲームパスが見つかりません。「手動で指定」をクリック。",
    toastSavedPath: "パスを保存しました。",
    toastWrote: (n) => `${n} ファイルを書き込みました。`,
    toastBackedUp: (p) => `バックアップ: ${p}`,
    toastPickModel: "有効な元 model を選んでください。",
    slot: { helm: "頭", body: "胴", arm: "腕", leg: "脚", wst: "腰" },
    countSuffix: "件",
    thModFolder: "Mod フォルダ",
    thModelsDetected: "検出した model",
    promptGamePath: "nativePC を含む MHW インストールフォルダのパス:",
    noModsFound: "Mod フォルダがありません。",
    noModsOrArchive: "f_equip に Mod を置くか、mod_hepsy を含むアーカイブをドロップしてください。",
    confirmOverwriteArchive: "この装備用フォルダに既にファイルがあります。上書きしますか？",
    toastArchiveLoaded: "アーカイブを読み込みました。元 model を選んで適用してください。",
    toastBadArchiveType: ".zip / .7z / .rar のみ対応です。",
    errRequest: "通信に失敗しました",
    emptyParsedMod: "（標準の f_* ファイルがありません）",
  },
};

const LANG_KEY = "mhw-pl-ui-lang";
const LANG_CODES = ["en", "ja", "zh-Hans", "zh-Hant"];

function getLang() {
  const s = localStorage.getItem(LANG_KEY);
  if (s === "zh") return "zh-Hans";
  if (LANG_CODES.includes(s)) return s;
  return "zh-Hans";
}

let LANG = getLang();

function setLang(code) {
  if (code === "zh") code = "zh-Hans";
  if (!LANG_CODES.includes(code)) return;
  LANG = code;
  localStorage.setItem(LANG_KEY, code);
  document.documentElement.lang =
    code === "ja" ? "ja" : code === "zh-Hans" ? "zh-Hans" : code === "zh-Hant" ? "zh-Hant" : "en";
}

function isChineseUi() {
  return LANG === "zh-Hans" || LANG === "zh-Hant";
}

function t(key, ...args) {
  const pack = UI[LANG] || UI["zh-Hans"];
  let v = pack[key];
  if (v === undefined) v = UI.en[key];
  if (typeof v === "function") return v(...args);
  if (v !== undefined) return v;
  return key;
}

function armorDisplayName(row) {
  if (LANG === "ja" && row.name_ja) return row.name_ja;
  if (isChineseUi() && row.name_zh) return row.name_zh;
  return row.name || "";
}

function formatApplyTarget(row) {
  const dn = armorDisplayName(row);
  if (LANG === "en") return `Target: [${row.id}] ${dn} → ${row.model_path}`;
  if (LANG === "ja") return `対象: [${row.id}] ${dn} → ${row.model_path}`;
  if (LANG === "zh-Hant") return `目標: [${row.id}] ${dn} → ${row.model_path}`;
  return `目标: [${row.id}] ${dn} → ${row.model_path}`;
}

function armorSearchText(row) {
  const parts = [row.name, row.name_zh, row.name_ja, String(row.id), row.model_path].filter(Boolean);
  const mp = row.model_path;
  if (mp && typeof mp === "string") {
    const m = /^pl(\d{3})_/i.exec(mp.trim());
    if (m) {
      parts.push(m[1], String(parseInt(m[1], 10)));
    }
  }
  return parts.join(" ").toLowerCase();
}

function armorBlobWithoutModelPath(row) {
  const parts = [row.name, row.name_zh, row.name_ja, String(row.id)].filter(Boolean);
  return parts.join(" ").toLowerCase();
}

/**
 * Supports plain 1–3 digit queries against the plXXX segment of model_path (e.g. 029 or 29),
 * without false positives from the four-digit variant (e.g. 105 inside …_5105).
 */
function armorMatchesQuery(row, q) {
  if (!q || !String(q).trim()) return true;
  const ql = String(q).trim().toLowerCase();
  if (/^\d{1,3}$/.test(ql)) {
    const n = parseInt(ql, 10);
    const mp = row.model_path;
    const m = mp && /^pl(\d{3})_/i.exec(String(mp).trim());
    if (m && parseInt(m[1], 10) === n) return true;
    if (String(row.id) === ql) return true;
    if (armorBlobWithoutModelPath(row).includes(ql)) return true;
    return false;
  }
  return armorSearchText(row).includes(ql);
}

function slotLabel(code) {
  const pack = UI[LANG] || UI["zh-Hans"];
  return pack.slot[code] || code;
}

function applyStaticI18n() {
  document.title = t("pageTitle");
  const h = document.getElementById("main-heading");
  if (h) h.textContent = t("heading");
  const sub = document.getElementById("main-sub");
  if (sub) sub.innerHTML = t("subHtml");
  const note = document.getElementById("lang-note");
  if (note) note.textContent = t("langNote");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (!key) return;
    const val = t(key);
    if (typeof val === "string") el.textContent = val;
  });

  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const key = el.getAttribute("data-i18n-html");
    if (key) el.innerHTML = t(key);
  });

  const ph = document.querySelector("#game-path");
  if (ph && !ph.value) ph.placeholder = t("pathPlaceholder");

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (key) el.placeholder = t(key);
  });

  const afs = document.getElementById("armor-filter-seg");
  if (afs) afs.setAttribute("aria-label", t("armorFilterGroup"));
}
