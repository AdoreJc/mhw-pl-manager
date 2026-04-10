const SLOTS = ["helm", "body", "arm", "leg", "wst"];

let armorRows = [];
let modsList = [];
let pendingTarget = null;
let armorFilter = "all";
/** @type {{ session_id: string, pl_candidates: string[], pl_sources: Record<string,string>, target_has_files: boolean } | null} */
let archiveImport = null;

function $(id) {
  return document.getElementById(id);
}

function toast(msg, err) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.remove("hidden", "err");
  if (err) el.classList.add("err");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add("hidden"), 5000);
}

async function api(path, opts) {
  const r = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(opts?.headers || {}) },
    ...opts,
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const d = data.detail;
    const msg =
      typeof d === "string"
        ? d
        : Array.isArray(d)
          ? d.map((x) => x.msg || JSON.stringify(x)).join("; ")
          : r.statusText || t("errRequest");
    throw new Error(msg);
  }
  return data;
}

function slotLabels(slots) {
  return SLOTS.map(
    (s) => `<span class="${slots[s] ? "on" : ""}">${escapeHtml(slotLabel(s))}</span>`
  ).join(" ");
}

async function refreshGame() {
  const g = await api("/api/game");
  const inp = $("game-path");
  if (g.game_root) {
    inp.value = g.game_root;
    $("layout-flags").innerHTML = [
      flag("nativePC", g.has_native_pc),
      flag("npc", g.has_npc),
      flag("pl", g.has_pl),
      flag("f_equip", g.has_f_equip),
    ].join("");
  } else {
    inp.value = "";
    $("layout-flags").innerHTML = `<span class="flag bad">${t("gameMissing")}</span>`;
  }
}

function flag(name, ok) {
  return `<span class="flag ${ok ? "ok" : "bad"}">${escapeHtml(layoutFlagLabel(name))}: ${
    ok ? t("flagYes") : t("flagNo")
  }</span>`;
}

function renderArmor() {
  const q = ($("filter-armor").value || "").toLowerCase();
  let rows = armorRows.filter((r) => !r.skipped && armorMatchesQuery(r, q));
  if (armorFilter === "missing") rows = rows.filter((r) => !r.has_mod);
  else if (armorFilter === "covered") rows = rows.filter((r) => r.has_mod);

  $("count-armor").textContent = `${rows.length} ${t("countSuffix")}`;

  $("tbody-armor").innerHTML = rows
    .map(
      (r) => `
    <tr>
      <td>${r.id}</td>
      <td>${escapeHtml(armorDisplayName(r))}${
        (isChineseUi() || LANG === "ja") && r.name
          ? `<br><small class="muted-en">${escapeHtml(r.name)}</small>`
          : ""
      }</td>
      <td><code>${escapeHtml(r.model_path)}</code></td>
      <td class="slots">${slotLabels(r.slots)}</td>
      <td>${escapeHtml(r.mods && r.mods.length ? r.mods.join(", ") : "—")}</td>
      <td>
        <button type="button" class="small primary btn-apply" data-id="${r.id}">${escapeHtml(t("btnApply"))}</button>
        ${
          r.has_mod
            ? ` <button type="button" class="small danger btn-remove" data-id="${r.id}">${escapeHtml(t("btnRemove"))}</button>`
            : ""
        }
      </td>
    </tr>`
    )
    .join("");

  document.querySelectorAll(".btn-apply").forEach((btn) => {
    btn.addEventListener("click", () => openApply(Number(btn.dataset.id)));
  });
  document.querySelectorAll(".btn-remove").forEach((btn) => {
    btn.addEventListener("click", () => openRemove(Number(btn.dataset.id)));
  });
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function clearArchiveImport() {
  archiveImport = null;
  $("apply-archive-block").classList.add("hidden");
  $("apply-installed-block").classList.remove("hidden");
  $("apply-archive-pl").innerHTML = "";
}

function setArchiveImport(data) {
  archiveImport = {
    session_id: data.session_id,
    pl_candidates: data.pl_candidates,
    pl_sources: data.pl_sources || {},
    target_has_files: data.target_has_files,
  };
  $("apply-installed-block").classList.add("hidden");
  $("apply-archive-block").classList.remove("hidden");
  const sel = $("apply-archive-pl");
  sel.innerHTML = data.pl_candidates
    .map((pl) => `<option value="${escapeHtml(pl)}">${escapeHtml(pl)}</option>`)
    .join("");
}

function isArchiveFilename(name) {
  const n = String(name || "").toLowerCase();
  return n.endsWith(".zip") || n.endsWith(".7z") || n.endsWith(".rar");
}

async function inspectArchiveUpload(file) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("target_model", pendingTarget?.model_path || "");
  const r = await fetch("/api/archive-mod-hepsy/inspect", { method: "POST", body: fd });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const d = data.detail;
    const msg =
      typeof d === "string"
        ? d
        : Array.isArray(d)
          ? d.map((x) => x.msg || JSON.stringify(x)).join("; ")
          : r.statusText || t("errRequest");
    throw new Error(msg);
  }
  return data;
}

function openApply(armorId) {
  const row = armorRows.find((r) => r.id === armorId);
  if (!row || !row.model_path) return;
  pendingTarget = row;
  clearArchiveImport();
  $("apply-target-line").textContent = formatApplyTarget(row);
  $("apply-output-line").textContent = t("dlgOutputFolder", row.model_path);
  $("apply-backup").checked = false;

  const modSel = $("apply-source-mod");
  const modelSel = $("apply-source-model");
  if (modsList.length === 0) {
    modSel.innerHTML = `<option value="">—</option>`;
    modSel.disabled = true;
    modelSel.innerHTML = `<option value="">${escapeHtml(t("emptyParsedMod"))}</option>`;
    modSel.onchange = null;
  } else {
    modSel.disabled = false;
    modSel.innerHTML = modsList
      .map((m) => `<option value="${escapeHtml(m.name)}">${escapeHtml(m.name)}</option>`)
      .join("");
    fillSourceModels();
    modSel.onchange = fillSourceModels;
  }

  $("dlg-apply").showModal();
}

function openRemove(armorId) {
  const row = armorRows.find((r) => r.id === armorId);
  if (!row || !row.model_path) return;
  pendingTarget = row;
  $("remove-target-line").textContent = formatApplyTarget(row);
  $("dlg-remove").showModal();
}

function fillSourceModels() {
  const name = $("apply-source-mod").value;
  const mod = modsList.find((m) => m.name === name);
  const sel = $("apply-source-model");
  const models = (mod && mod.models) || [];
  sel.innerHTML = models.map((pl) => `<option value="${pl}">${pl}</option>`).join("");
  if (models.length === 0) {
    sel.innerHTML = `<option value="">${escapeHtml(t("emptyParsedMod"))}</option>`;
  }
}

async function loadAll() {
  await refreshGame();
  try {
    const cov = await api("/api/armor/coverage");
    armorRows = cov.armor || [];
  } catch (e) {
    armorRows = [];
    toast(e.message || String(e), true);
  }
  try {
    const m = await api("/api/mods");
    modsList = m.mods || [];
    renderMods();
  } catch {
    modsList = [];
    renderMods();
  }
  renderArmor();
}

function renderMods() {
  $("tbody-mods").innerHTML = modsList
    .map(
      (m) => `
    <tr>
      <td><code>${escapeHtml(m.name)}</code></td>
      <td>${m.models.map((pl) => `<code>${escapeHtml(pl)}</code>`).join(" ")}</td>
    </tr>`
    )
    .join("");
}

function syncLangButtons() {
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    const on = btn.dataset.lang === LANG;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  });
}

function syncArmorFilterButtons() {
  document.querySelectorAll("[data-armor-filter]").forEach((btn) => {
    const on = btn.dataset.armorFilter === armorFilter;
    btn.classList.toggle("active", on);
  });
}

function initLangUi() {
  const seg = $("lang-seg");
  if (!seg) return;
  syncLangButtons();
  seg.addEventListener("click", (e) => {
    const btn = e.target.closest(".lang-btn");
    if (!btn || !btn.dataset.lang) return;
    setLang(btn.dataset.lang);
    syncLangButtons();
    applyStaticI18n();
    void refreshGame();
    renderArmor();
    renderMods();
  });
}

function initArmorFilterUi() {
  const seg = $("armor-filter-seg");
  if (!seg) return;
  seg.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-armor-filter]");
    if (!btn || !btn.dataset.armorFilter) return;
    armorFilter = btn.dataset.armorFilter;
    syncArmorFilterButtons();
    renderArmor();
  });
}

$("filter-armor").addEventListener("input", renderArmor);

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));
    $(`tab-${tab.dataset.tab}`).classList.remove("hidden");
  });
});

$("btn-browse").addEventListener("click", async () => {
  const path = window.prompt(t("promptGamePath"), $("game-path").value || "");
  if (!path || !path.trim()) return;
  try {
    await api("/api/game", { method: "POST", body: JSON.stringify({ path: path.trim() }) });
    toast(t("toastSavedPath"));
    await loadAll();
  } catch (e) {
    toast(e.message || String(e), true);
  }
});

function initApplyDropZone() {
  const dz = $("apply-drop-zone");
  if (!dz) return;
  const onOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dz.classList.add("dragover");
  };
  const onLeave = (e) => {
    e.preventDefault();
    dz.classList.remove("dragover");
  };
  dz.addEventListener("dragenter", onOver);
  dz.addEventListener("dragover", onOver);
  dz.addEventListener("dragleave", onLeave);
  dz.addEventListener("drop", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    dz.classList.remove("dragover");
    if (!pendingTarget) return;
    const f = e.dataTransfer?.files?.[0];
    if (!f) return;
    if (!isArchiveFilename(f.name)) {
      toast(t("toastBadArchiveType"), true);
      return;
    }
    try {
      const data = await inspectArchiveUpload(f);
      if (!data.ok || !data.session_id) {
        toast(data.error || t("errRequest"), true);
        return;
      }
      setArchiveImport(data);
      toast(t("toastArchiveLoaded"));
    } catch (err) {
      toast(err.message || String(err), true);
    }
  });
}

$("apply-clear-archive").addEventListener("click", () => {
  clearArchiveImport();
  const modSel = $("apply-source-mod");
  if (modsList.length) {
    modSel.disabled = false;
    modSel.innerHTML = modsList
      .map((m) => `<option value="${escapeHtml(m.name)}">${escapeHtml(m.name)}</option>`)
      .join("");
    fillSourceModels();
    modSel.onchange = fillSourceModels;
  } else {
    modSel.innerHTML = `<option value="">—</option>`;
    modSel.disabled = true;
    $("apply-source-model").innerHTML = `<option value="">${escapeHtml(t("emptyParsedMod"))}</option>`;
    modSel.onchange = null;
  }
});

$("form-apply").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!pendingTarget) return;
  const backup_existing = $("apply-backup").checked;

  if (archiveImport) {
    const source_pl = $("apply-archive-pl").value;
    if (!source_pl) {
      toast(t("toastPickModel"), true);
      return;
    }
    let overwrite = false;
    if (archiveImport.target_has_files) {
      if (!window.confirm(t("confirmOverwriteArchive"))) return;
      overwrite = true;
    }
    try {
      const res = await api("/api/archive-mod-hepsy/apply", {
        method: "POST",
        body: JSON.stringify({
          session_id: archiveImport.session_id,
          source_pl,
          source_prefix: archiveImport.pl_sources[source_pl] || "",
          target_model: pendingTarget.model_path,
          backup_existing,
          overwrite,
        }),
      });
      let msg = t("toastWrote", res.count);
      if (res.backup_path) msg += " " + t("toastBackedUp", res.backup_path);
      toast(msg);
      clearArchiveImport();
      $("dlg-apply").close();
      await loadAll();
    } catch (err) {
      toast(err.message || String(err), true);
    }
    return;
  }

  const source_mod = $("apply-source-mod").value;
  const source_model = $("apply-source-model").value;
  if (!modsList.length) {
    toast(t("noModsOrArchive"), true);
    return;
  }
  if (!source_model) {
    toast(t("toastPickModel"), true);
    return;
  }
  try {
    const res = await api("/api/apply-mod", {
      method: "POST",
      body: JSON.stringify({
        source_mod,
        source_model,
        target_model: pendingTarget.model_path,
        backup_existing,
      }),
    });
    let msg = t("toastWrote", res.count);
    if (res.backup_path) msg += " " + t("toastBackedUp", res.backup_path);
    toast(msg);
    $("dlg-apply").close();
    await loadAll();
  } catch (err) {
    toast(err.message || String(err), true);
  }
});

$("apply-cancel").addEventListener("click", () => $("dlg-apply").close());

$("dlg-apply").addEventListener("close", () => {
  clearArchiveImport();
});

async function doRemove(backup_before_remove) {
  if (!pendingTarget || !pendingTarget.model_path) return;
  try {
    const res = await api("/api/remove-mod", {
      method: "POST",
      body: JSON.stringify({
        target_model: pendingTarget.model_path,
        backup_before_remove,
      }),
    });
    let msg = t("btnRemove");
    if (res.backup_path) msg += " " + t("toastBackedUp", res.backup_path);
    toast(msg);
    $("dlg-remove").close();
    await loadAll();
  } catch (err) {
    toast(err.message || String(err), true);
  }
}

$("btn-remove-backup").addEventListener("click", () => doRemove(true));
$("btn-remove-nobackup").addEventListener("click", () => doRemove(false));

setLang(getLang());
initLangUi();
initArmorFilterUi();
initApplyDropZone();
syncArmorFilterButtons();
applyStaticI18n();
loadAll().catch((e) => toast(e.message || String(e), true));
