// ==========================================================================
// HORA CHART - OBSIDIAN STUDIO CONTROLLER (MILLISECOND PRECISION v9.0)
// ==========================================================================

const RASI_SHORT_NAMES = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"];
const RASI_FULL_NAMES = [
  "Aries (Mesham)", "Taurus (Rishabham)", "Gemini (Mithunam)", "Cancer (Kadagam)",
  "Leo (Simmam)", "Virgo (Kanni)", "Libra (Thulaam)", "Scorpio (Viruchigam)",
  "Sagittarius (Dhanusu)", "Capricorn (Magaram)", "Aquarius (Kumbam)", "Pisces (Meenam)"
];

const PLANET_SHORT_NAMES = {
  "Sun": "SU",
  "Moon": "MO",
  "Mars": "MA",
  "Mercury": "ME",
  "Jupiter": "JU",
  "Venus": "VE",
  "Saturn": "SA",
  "Snake": "SN"
};

const PLANET_SYMBOLS = {
  "Sun": "☉",
  "Moon": "☽",
  "Mars": "♂",
  "Mercury": "☿",
  "Jupiter": "♃",
  "Venus": "♀",
  "Saturn": "♄",
  "Snake": "☊",
  "Rahu": "☊",
  "Ketu": "☋"
};

const STATE = {
  // Captured / Active Chart state (Right Side + Tables + PDF Export)
  currentDateTime: new Date(),
  latestHoroscopeData: null,
  activeVarga: "main",

  // Live Running Chart state (Left Side - constantly ticking with ms)
  liveDateTime: new Date(),
  liveHoroscopeData: null,
  isFetchingLive: false,
  liveTimerId: null,
  liveClockTickerId: null,

  // Captured Moments Vault (Local .md Files on Disk + Session History)
  vaultNotes: [],
  activeVaultFilename: "",
  vaultSearchQuery: "",
  vaultDir: "",
  codeMirrorEditor: null,
  cmdSelectedIndex: 0,

  // Shared Location & Calculation Settings
  latitude: 12.98117,
  longitude: 77.48509,
  altitude: 820.0,
  cityName: "Bedarahalli, Bengaluru, Karnataka 560091",
  timeOffset: 5.5,
  method: "vedic",
  houseIndexMode: "1to12",
  clientName: "Rajagopal",
  clientNotes: ""
};

// ==========================================================================
// 1. INITIALIZATION & LIFECYCLE (ELECTRON + VANILLA JS + CODEMIRROR)
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  initCodeMirrorEditor();
  setupElectronShellIfPresent();
  setupEventListeners();
  setupCommandPalette();
  loadVaultNotesFromDisk();
  initAutoGps();

  const now = new Date();
  STATE.liveDateTime = new Date(now);
  STATE.currentDateTime = new Date(now);

  fetchLiveHoroscope(true); // true = also initialize captured chart on first load
  startLiveChartLoop();
});

function initCodeMirrorEditor() {
  const textarea = document.getElementById("codemirrorMarkdownInput");
  if (!textarea) return;

  if (window.CodeMirror) {
    STATE.codeMirrorEditor = window.CodeMirror.fromTextArea(textarea, {
      mode: "markdown",
      lineNumbers: true,
      lineWrapping: true,
      extraKeys: {
        "Ctrl-S": () => saveActiveEditorMarkdownToVault(),
        "Cmd-S": () => saveActiveEditorMarkdownToVault()
      }
    });
  }
}

async function setupElectronShellIfPresent() {
  const isElectron = Boolean(window.obsidianAPI && window.obsidianAPI.isElectron);
  const winCtrls = document.getElementById("electronWindowControls");
  const btnSelectFolder = document.getElementById("btnSelectVaultFolder");
  const btnOpenExplorer = document.getElementById("btnOpenVaultExplorer");
  const stackBadge = document.getElementById("stackBadgePill");

  if (isElectron) {
    if (winCtrls) winCtrls.style.display = "inline-flex";
    if (btnSelectFolder) btnSelectFolder.style.display = "inline-block";
    if (btnOpenExplorer) btnOpenExplorer.style.display = "inline-flex";
    if (stackBadge) stackBadge.innerText = "Electron + CodeMirror";

    const btnMin = document.getElementById("btnWinMin");
    const btnMax = document.getElementById("btnWinMax");
    const btnClose = document.getElementById("btnWinClose");
    if (btnMin) btnMin.addEventListener("click", () => window.obsidianAPI.minimizeWindow());
    if (btnMax) btnMax.addEventListener("click", () => window.obsidianAPI.maximizeWindow());
    if (btnClose) btnClose.addEventListener("click", () => window.obsidianAPI.closeWindow());

    if (btnSelectFolder) {
      btnSelectFolder.addEventListener("click", async () => {
        const info = await window.obsidianAPI.selectVaultFolder();
        if (info && info.vault_dir) {
          STATE.vaultDir = info.vault_dir;
          await loadVaultNotesFromDisk();
        }
      });
    }

    if (btnOpenExplorer) {
      btnOpenExplorer.addEventListener("click", () => window.obsidianAPI.openVaultInExplorer());
    }
  } else {
    if (stackBadge) stackBadge.innerText = "Obsidian Stack + CodeMirror";
  }
}

function startLiveChartLoop() {
  if (STATE.liveTimerId) clearInterval(STATE.liveTimerId);
  if (STATE.liveClockTickerId) clearInterval(STATE.liveClockTickerId);

  // High-frequency millisecond display ticker (every 55ms so .mmm visibly spins)
  STATE.liveClockTickerId = setInterval(() => {
    const now = new Date();
    STATE.liveDateTime = now;
    const liveClockEl = document.getElementById("liveHeaderClock");
    if (liveClockEl) {
      liveClockEl.innerText = formatDateToCustomString(now, true);
    }
    const liveSubEl = document.getElementById("live-centerTimeSubtitle");
    if (liveSubEl && STATE.liveHoroscopeData) {
      const jamamInfo = STATE.liveHoroscopeData.jamam_info || {};
      const tzFormatted = formatTzOffset(STATE.timeOffset);
      liveSubEl.innerText = `${jamamInfo.day_name || ''}, ${formatDateToCustomString(now, true)} (${tzFormatted})`;
    }
  }, 55);

  // Ephemeris & Arudham/Udhayam refresh loop (every 500ms for responsive sub-second updates)
  STATE.liveTimerId = setInterval(() => {
    STATE.liveDateTime = new Date();
    fetchLiveHoroscope(false);
  }, 500);
}

function setupEventListeners() {
  // CLICK ON LIVE RUNNING CHART (LEFT) -> CAPTURE EXACT MILLISECOND MOMENT TO RIGHT CHART
  const liveChartFrame = document.getElementById("liveChartFrame");
  if (liveChartFrame) {
    liveChartFrame.addEventListener("click", () => {
      captureLiveMomentToRight();
    });
  }

  // Navigation step buttons (control Captured Chart on Right)
  document.getElementById("btnStepPrev").addEventListener("click", () => stepTime(-1));
  document.getElementById("btnStepNext").addEventListener("click", () => stepTime(1));
  document.getElementById("btnNow").addEventListener("click", () => {
    captureLiveMomentToRight();
  });

  // Obsidian Left Ribbon Controls
  const btnNavCharts = document.getElementById("btnNavCharts");
  if (btnNavCharts) {
    btnNavCharts.addEventListener("click", () => {
      document.getElementById("topChartWorkspace").scrollIntoView({ behavior: "smooth" });
    });
  }

  const btnNavTables = document.getElementById("btnNavTables");
  if (btnNavTables) {
    btnNavTables.addEventListener("click", () => {
      document.getElementById("printSectionKp").scrollIntoView({ behavior: "smooth" });
    });
  }

  const btnNavEditor = document.getElementById("btnNavEditor");
  if (btnNavEditor) {
    btnNavEditor.addEventListener("click", () => {
      const edSec = document.getElementById("markdownEditorSection");
      if (edSec) edSec.scrollIntoView({ behavior: "smooth" });
      if (STATE.codeMirrorEditor) STATE.codeMirrorEditor.focus();
    });
  }

  const btnToggleVault = document.getElementById("btnToggleVault");
  const vaultDrawer = document.getElementById("vaultDrawer");
  if (btnToggleVault && vaultDrawer) {
    btnToggleVault.addEventListener("click", () => {
      vaultDrawer.classList.toggle("open");
      btnToggleVault.classList.toggle("active", vaultDrawer.classList.contains("open"));
    });
  }

  const btnNewVaultNote = document.getElementById("btnNewVaultNote");
  if (btnNewVaultNote) {
    btnNewVaultNote.addEventListener("click", () => {
      if (STATE.latestHoroscopeData) {
        saveCapturedChartToVaultMd(STATE.latestHoroscopeData, false);
      }
    });
  }

  const btnSaveMarkdownVault = document.getElementById("btnSaveMarkdownVault");
  if (btnSaveMarkdownVault) {
    btnSaveMarkdownVault.addEventListener("click", () => {
      if (STATE.latestHoroscopeData) {
        saveCapturedChartToVaultMd(STATE.latestHoroscopeData, false);
      }
    });
  }

  const btnSaveEditorMd = document.getElementById("btnSaveEditorMd");
  if (btnSaveEditorMd) {
    btnSaveEditorMd.addEventListener("click", () => {
      saveActiveEditorMarkdownToVault();
    });
  }

  const vaultSearchInp = document.getElementById("vaultSearchInput");
  if (vaultSearchInp) {
    vaultSearchInp.addEventListener("input", (e) => {
      STATE.vaultSearchQuery = (e.target.value || "").trim().toLowerCase();
      renderVaultList();
    });
  }

  const btnToggleChartTheme = document.getElementById("btnToggleChartTheme");
  if (btnToggleChartTheme) {
    btnToggleChartTheme.addEventListener("click", () => {
      document.body.classList.toggle("chart-theme-dark");
      btnToggleChartTheme.classList.toggle("active", document.body.classList.contains("chart-theme-dark"));
    });
  }

  const btnToggleAppTheme = document.getElementById("btnToggleAppTheme");
  if (btnToggleAppTheme) {
    btnToggleAppTheme.addEventListener("click", () => {
      document.body.classList.toggle("obsidian-light");
      btnToggleAppTheme.classList.toggle("active", document.body.classList.contains("obsidian-light"));
    });
  }

  const btnRibbonPdf = document.getElementById("btnRibbonPdf");
  if (btnRibbonPdf) btnRibbonPdf.addEventListener("click", handleSavePdf);

  // GPS button
  document.getElementById("btnGps").addEventListener("click", () => initAutoGps(true));

  // Date Picker
  const datePickerBtn = document.getElementById("btnDatePicker");
  const hiddenInput = document.getElementById("hiddenDateTimeInput");
  datePickerBtn.addEventListener("click", () => {
    hiddenInput.value = formatDateTimeLocal(STATE.currentDateTime);
    hiddenInput.showPicker ? hiddenInput.showPicker() : hiddenInput.click();
  });
  hiddenInput.addEventListener("change", (e) => {
    if (e.target.value) {
      STATE.currentDateTime = new Date(e.target.value);
      fetchAndRenderCapturedHoroscope(true);
    }
  });

  // Settings Modal
  const modal = document.getElementById("settingsModal");
  const openSettingsModal = () => {
    document.getElementById("cfgCityName").value = STATE.cityName;
    document.getElementById("cfgLat").value = STATE.latitude;
    document.getElementById("cfgLon").value = STATE.longitude;
    document.getElementById("cfgAlt").value = STATE.altitude;
    document.getElementById("cfgTz").value = STATE.timeOffset;
    document.getElementById("cfgMethod").value = STATE.method;
    document.getElementById("cfgHouseIndexMode").value = STATE.houseIndexMode;
    modal.classList.add("open");
  };

  document.getElementById("btnSettings").addEventListener("click", openSettingsModal);
  const btnRibbonSettings = document.getElementById("btnRibbonSettings");
  if (btnRibbonSettings) btnRibbonSettings.addEventListener("click", openSettingsModal);

  document.getElementById("btnCloseSettings").addEventListener("click", () => modal.classList.remove("open"));
  document.getElementById("btnCancelSettings").addEventListener("click", () => modal.classList.remove("open"));
  
  document.getElementById("btnSaveSettings").addEventListener("click", () => {
    STATE.cityName = document.getElementById("cfgCityName").value;
    STATE.latitude = parseFloat(document.getElementById("cfgLat").value) || 12.98117;
    STATE.longitude = parseFloat(document.getElementById("cfgLon").value) || 77.48509;
    STATE.altitude = parseFloat(document.getElementById("cfgAlt").value) || 820.0;
    STATE.timeOffset = parseFloat(document.getElementById("cfgTz").value) || 5.5;
    STATE.method = document.getElementById("cfgMethod").value.toLowerCase();
    STATE.houseIndexMode = document.getElementById("cfgHouseIndexMode").value;
    modal.classList.remove("open");
    fetchLiveHoroscope(false);
    fetchAndRenderCapturedHoroscope(false);
  });

  // Save / Export PDF Buttons & Client Name Sync
  const btnSavePdf = document.getElementById("btnSavePdf");
  if (btnSavePdf) btnSavePdf.addEventListener("click", handleSavePdf);

  const btnToolbarPdf = document.getElementById("btnToolbarPdf");
  if (btnToolbarPdf) btnToolbarPdf.addEventListener("click", handleSavePdf);

  const clientNameInp = document.getElementById("clientNameInput");
  if (clientNameInp) {
    clientNameInp.addEventListener("input", () => syncPdfDocumentTitle());
    clientNameInp.addEventListener("change", () => syncPdfDocumentTitle());
  }

  // Direct Date & Time Toolbar Inputs (with millisecond support)
  const handleToolbarDateChange = () => {
    const day = parseInt(document.getElementById("inpDay").value) || 1;
    const month = parseInt(document.getElementById("inpMonth").value) || 0;
    const year = parseInt(document.getElementById("inpYear").value) || 2026;
    const timeVal = document.getElementById("inpTime").value || "00:00:00.000";
    const [hmsPart, msPart] = timeVal.split(".");
    const parts = (hmsPart || "00:00:00").split(":").map(n => parseInt(n) || 0);
    const hh = parts[0] || 0;
    const mm = parts[1] || 0;
    const ss = parts[2] || 0;
    const ms = msPart ? parseInt(msPart.padEnd(3, "0").slice(0, 3)) || 0 : 0;

    const d = new Date(year, month, day, hh, mm, ss, ms);
    STATE.currentDateTime = d;
    fetchAndRenderCapturedHoroscope(true);
  };

  ["inpDay", "inpMonth", "inpYear", "inpTime"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", handleToolbarDateChange);
  });

  const cityToolbarInp = document.getElementById("inpCityToolbar");
  if (cityToolbarInp) {
    cityToolbarInp.addEventListener("change", (e) => {
      STATE.cityName = e.target.value.trim();
      renderLiveChartFromState();
      renderCapturedChartFromState();
    });
    cityToolbarInp.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        STATE.cityName = e.target.value.trim();
        cityToolbarInp.blur();
        renderLiveChartFromState();
        renderCapturedChartFromState();
      }
    });
  }

  // View tabs (for Captured Chart)
  document.querySelectorAll(".view-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".view-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      STATE.activeVarga = tab.getAttribute("data-varga");
      document.getElementById("allVargasSelect").value = STATE.activeVarga;
      updateCapturedVargaBadge();
      renderCapturedChartFromState();
    });
  });

  // Varga dropdown (for Captured Chart)
  document.getElementById("allVargasSelect").addEventListener("change", (e) => {
    const val = e.target.value;
    STATE.activeVarga = val;
    document.querySelectorAll(".view-tab").forEach(t => {
      if (t.getAttribute("data-varga") === val) {
        t.classList.add("active");
      } else {
        t.classList.remove("active");
      }
    });
    updateCapturedVargaBadge();
    renderCapturedChartFromState();
  });
}

function updateCapturedVargaBadge() {
  const badge = document.getElementById("capturedVargaBadge");
  if (!badge) return;
  if (STATE.activeVarga === "main") {
    badge.innerText = "Hora Chart";
  } else {
    const sel = document.getElementById("allVargasSelect");
    const opt = sel ? sel.querySelector(`option[value="${STATE.activeVarga}"]`) : null;
    badge.innerText = opt ? opt.textContent.split("(")[0].trim() : STATE.activeVarga.toUpperCase();
  }
}

// ==========================================================================
// 2. CAPTURE EXACT MILLISECOND MOMENT TO RIGHT-SIDE CHART & VAULT
// ==========================================================================

function captureLiveMomentToRight() {
  const exactClickMoment = new Date();
  STATE.currentDateTime = exactClickMoment;

  // Visual flash on the Right Captured Chart frame
  const rightFrame = document.getElementById("mainChartFrame");
  if (rightFrame) {
    rightFrame.classList.remove("capture-flash");
    void rightFrame.offsetWidth;
    rightFrame.classList.add("capture-flash");
  }

  // Immediately render the latest live snapshot with the exact clicked millisecond timestamp,
  // and also fetch exact sub-second ephemeris/arudham from the backend for this exact millisecond!
  if (STATE.liveHoroscopeData) {
    const instantCopy = JSON.parse(JSON.stringify(STATE.liveHoroscopeData));
    instantCopy.datetime_local = formatDateTimeLocal(exactClickMoment);
    STATE.latestHoroscopeData = instantCopy;
    renderCapturedChartFromState();
  }

  fetchAndRenderCapturedHoroscope(true);
}

function addSnapshotToVault(data) {
  if (!data) return;
  saveCapturedChartToVaultMd(data, true);
}

function buildMarkdownFilename(data) {
  const clientNameEl = document.getElementById("clientNameInput");
  const clientName = ((clientNameEl ? clientNameEl.value.trim() : "") || "Rajagopal").replace(/[^a-zA-Z0-9_-]/g, "_");
  const dt = data && data.datetime_local ? new Date(data.datetime_local) : STATE.currentDateTime;
  const timePart = formatDateToCustomString(dt, true).replace(/:/g, "-").replace(/\s+/g, "_");
  return `${clientName}_${timePart}.md`;
}

function buildMarkdownFromHoroscope(data, customNotesText = null) {
  const dt = new Date(data.datetime_local);
  const timeFormatted = formatDateToCustomString(dt, true);
  const clientNameEl = document.getElementById("clientNameInput");
  const clientNotesEl = document.getElementById("clientNotesInput");
  const querent = (clientNameEl ? clientNameEl.value.trim() : "") || "Rajagopal";
  const shortQuery = customNotesText !== null
    ? customNotesText
    : ((clientNotesEl ? clientNotesEl.value.trim() : "") || "General Jamakkol Horary Prasanam consultation.");

  const main = data.main_chart || {};
  const u = main.udhayam ? main.udhayam.housedetails : {};
  const ar = main.arudham || {};
  const kv = main.kavippu || {};
  const asc = main.ascendant_sidereal ? main.ascendant_sidereal.housedetails : {};
  const jamam = data.jamam_info || {};
  const hora = data.hora_info || {};

  const p = main.planets || {};
  const pOrder = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"];
  const pRows = pOrder.map((k) => {
    const obj = p[k];
    if (!obj || !obj.housedetails) return "";
    const hd = obj.housedetails;
    const kp = hd.kp_details || {};
    const name = k.charAt(0).toUpperCase() + k.slice(1);
    return `| **${name}** | ${hd.rasi} | H${hd.house} | \`${hd.DMS}\` | ${kp.nakshatra_name_en || "-"}-${kp.pada || 1} | ${kp.star_lord || "-"} / **${kp.sub_lord || "-"}** |`;
  }).filter(Boolean).join("\n");

  return [
    "---",
    `querent: "${querent}"`,
    `captured_iso_ms: "${data.datetime_local}"`,
    `display_time: "${timeFormatted}"`,
    `location: "${STATE.cityName}"`,
    `latitude: ${STATE.latitude}`,
    `longitude: ${STATE.longitude}`,
    `jamam: "${jamam.day_name || ""} Jamam #${jamam.jamam_number || ""}"`,
    `hora: "${hora.hora_lord || ""}"`,
    `udhayam: "${u.rasi || ""} (${u.DMS || ""})"`,
    `arudham: "${ar.rasi || ""} (${ar.DMS || ""})"`,
    `kavippu: "${kv.rasi || ""} (${kv.DMS || ""})"`,
    "tags:",
    "  - jamakkol-prasanam",
    "  - horary-consultation",
    "---",
    "",
    `# 🔮 Horary Reading: [[${querent}]] — ${timeFormatted}`,
    "",
    `- **Location**: ${STATE.cityName} (\`${STATE.latitude.toFixed(5)}, ${STATE.longitude.toFixed(5)}\`)`,
    `- **Jamam & Hora**: ${jamam.display_title || "HORA CHART"} | ${hora.hora_display || ""}`,
    `- **Udhayam (UD)**: **${u.rasi || "-"}** (\`${u.DMS || "-"}\`) | **Arudham (AR)**: **${ar.rasi || "-"}** (\`${ar.DMS || "-"}\`) | **Kavippu (KV)**: **${kv.rasi || "-"}** (\`${kv.DMS || "-"}\`)`,
    `- **Ascendant (ASC)**: **${asc.rasi || "-"}** (\`${asc.DMS || "-"}\`)`,
    "",
    "## 📝 Query & Astrological Prediction Notes",
    shortQuery,
    "",
    "- Related Readings: [[Jamakkol Rules]] • [[Udhayam Significations]] • [[Arudham Analysis]]",
    "",
    "## 🪐 Planetary Placements & KP Sub-Lords",
    "| Body | Rasi | House | Degree (DMS) | Nakshatra | Star / Sub Lord |",
    "| :--- | :--- | :---: | :--- | :--- | :--- |",
    pRows,
    "",
    "```horary-snapshot",
    JSON.stringify(data),
    "```",
    ""
  ].join("\n");
}

async function saveCapturedChartToVaultMd(data, isAutoCapture = false) {
  if (!data) return;
  const filename = buildMarkdownFilename(data);
  const mdContent = buildMarkdownFromHoroscope(data);

  STATE.activeVaultFilename = filename;
  const filePill = document.getElementById("activeMarkdownFilename");
  if (filePill) filePill.innerText = filename;
  const tabBreadcrumb = document.getElementById("activeTabBreadcrumb");
  if (tabBreadcrumb) tabBreadcrumb.innerText = `HoraryVault / ${filename}`;

  if (STATE.codeMirrorEditor) {
    STATE.codeMirrorEditor.setValue(mdContent);
  } else {
    const rawTa = document.getElementById("codemirrorMarkdownInput");
    if (rawTa) rawTa.value = mdContent;
  }

  try {
    if (window.obsidianAPI && window.obsidianAPI.isElectron) {
      await window.obsidianAPI.saveVaultNote(filename, mdContent);
    } else {
      await fetch("/api/vault/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, markdown_content: mdContent })
      });
    }
    const statusBadge = document.getElementById("vaultSaveStatusBadge");
    if (statusBadge) {
      statusBadge.innerText = isAutoCapture ? `Auto-saved ${filename}` : `Saved ${filename} to Vault`;
    }
    await loadVaultNotesFromDisk();
  } catch (err) {
    console.warn("Could not save .md note to disk vault:", err);
  }
}

async function saveActiveEditorMarkdownToVault() {
  const filename = STATE.activeVaultFilename || buildMarkdownFilename(STATE.latestHoroscopeData);
  const mdContent = STATE.codeMirrorEditor
    ? STATE.codeMirrorEditor.getValue()
    : (document.getElementById("codemirrorMarkdownInput")?.value || "");

  if (!mdContent.trim()) return;

  try {
    if (window.obsidianAPI && window.obsidianAPI.isElectron) {
      await window.obsidianAPI.saveVaultNote(filename, mdContent);
    } else {
      await fetch("/api/vault/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, markdown_content: mdContent })
      });
    }
    const statusBadge = document.getElementById("vaultSaveStatusBadge");
    if (statusBadge) statusBadge.innerText = `Saved ${filename} ✓`;
    await loadVaultNotesFromDisk();
  } catch (err) {
    console.error("Failed to save editor markdown:", err);
  }
}

async function loadVaultNotesFromDisk() {
  try {
    let resData = null;
    if (window.obsidianAPI && window.obsidianAPI.isElectron) {
      resData = await window.obsidianAPI.listVaultNotes();
    } else {
      const resp = await fetch("/api/vault/notes");
      if (resp.ok) resData = await resp.json();
    }
    if (resData) {
      STATE.vaultDir = resData.vault_dir || "";
      STATE.vaultNotes = resData.notes || [];
      const pathSub = document.getElementById("vaultFolderPathSub");
      if (pathSub && STATE.vaultDir) {
        pathSub.innerText = `Vault: ${STATE.vaultDir}`;
      }
      renderVaultList();
    }
  } catch (err) {
    console.warn("Vault list error:", err);
  }
}

async function openVaultNoteByFilename(filename) {
  try {
    let noteObj = null;
    if (window.obsidianAPI && window.obsidianAPI.isElectron) {
      noteObj = await window.obsidianAPI.readVaultNote(filename);
    } else {
      const resp = await fetch(`/api/vault/read?filename=${encodeURIComponent(filename)}`);
      if (resp.ok) noteObj = await resp.json();
    }
    if (!noteObj || !noteObj.markdown_content) return;

    STATE.activeVaultFilename = noteObj.filename;
    const filePill = document.getElementById("activeMarkdownFilename");
    if (filePill) filePill.innerText = noteObj.filename;
    const tabBreadcrumb = document.getElementById("activeTabBreadcrumb");
    if (tabBreadcrumb) tabBreadcrumb.innerText = `HoraryVault / ${noteObj.filename}`;

    if (STATE.codeMirrorEditor) {
      STATE.codeMirrorEditor.setValue(noteObj.markdown_content);
    } else {
      const rawTa = document.getElementById("codemirrorMarkdownInput");
      if (rawTa) rawTa.value = noteObj.markdown_content;
    }

    // Parse querent from YAML frontmatter if present
    const querentMatch = noteObj.markdown_content.match(/^querent:\s*"([^"]+)"/m);
    if (querentMatch && document.getElementById("clientNameInput")) {
      document.getElementById("clientNameInput").value = querentMatch[1];
    }

    // Extract embedded ```horary-snapshot JSON block to restore the exact chart!
    const snapMatch = noteObj.markdown_content.match(/```horary-snapshot\s*([\s\S]*?)```/);
    if (snapMatch && snapMatch[1]) {
      const parsedChart = JSON.parse(snapMatch[1].trim());
      STATE.latestHoroscopeData = parsedChart;
      if (parsedChart.datetime_local) {
        STATE.currentDateTime = new Date(parsedChart.datetime_local);
      }
      renderCapturedChartFromState();
    }
    renderVaultList();
  } catch (err) {
    console.error("Failed to open vault .md note:", err);
  }
}

async function deleteVaultNoteByFilename(filename, ev) {
  if (ev) ev.stopPropagation();
  try {
    if (window.obsidianAPI && window.obsidianAPI.isElectron) {
      await window.obsidianAPI.deleteVaultNote(filename);
    } else {
      await fetch(`/api/vault/delete?filename=${encodeURIComponent(filename)}`, { method: "DELETE" });
    }
    await loadVaultNotesFromDisk();
  } catch (err) {
    console.error("Failed to delete vault note:", err);
  }
}

function renderVaultList() {
  const listEl = document.getElementById("vaultHistoryList");
  const badgeEl = document.getElementById("vaultCountBadge");
  if (badgeEl) badgeEl.innerText = STATE.vaultNotes.length;
  if (!listEl) return;

  listEl.innerHTML = "";
  const q = STATE.vaultSearchQuery;
  const filtered = STATE.vaultNotes.filter((n) => {
    if (!q) return true;
    return n.filename.toLowerCase().includes(q) || (n.preview && n.preview.toLowerCase().includes(q));
  });

  filtered.forEach((note) => {
    const item = document.createElement("div");
    const isActive = note.filename === STATE.activeVaultFilename;
    item.className = `vault-item${isActive ? " active" : ""}`;

    // Extract UD / AR from YAML preview if present
    const udMatch = (note.preview || "").match(/udhayam:\s*"([^"]+)"/);
    const arMatch = (note.preview || "").match(/arudham:\s*"([^"]+)"/);
    const metaStr = (udMatch || arMatch)
      ? `UD: ${udMatch ? udMatch[1].split(" ")[0] : "-"} • AR: ${arMatch ? arMatch[1].split(" ")[0] : "-"}`
      : "Markdown Consultation (.md)";

    item.innerHTML = `
      <div class="vault-item-top">
        <div class="vault-item-time">📄 ${note.filename}</div>
        <button class="vault-del-btn" title="Delete .md file from Vault">&times;</button>
      </div>
      <div class="vault-item-meta">${metaStr}</div>
    `;

    const delBtn = item.querySelector(".vault-del-btn");
    if (delBtn) {
      delBtn.addEventListener("click", (ev) => deleteVaultNoteByFilename(note.filename, ev));
    }

    item.addEventListener("click", () => {
      openVaultNoteByFilename(note.filename);
    });
    listEl.appendChild(item);
  });
}

// ==========================================================================
// 3. TIME STEPPING ENGINE (INCLUDING 100ms AND 1s)
// ==========================================================================

function stepTime(direction) {
  const unit = document.getElementById("stepUnit").value;
  const d = new Date(STATE.currentDateTime);

  switch (unit) {
    case "100ms": d.setMilliseconds(d.getMilliseconds() + (100 * direction)); break;
    case "1s": d.setSeconds(d.getSeconds() + (1 * direction)); break;
    case "1m": d.setMinutes(d.getMinutes() + (1 * direction)); break;
    case "5m": d.setMinutes(d.getMinutes() + (5 * direction)); break;
    case "15m": d.setMinutes(d.getMinutes() + (15 * direction)); break;
    case "1j": d.setMinutes(d.getMinutes() + (90 * direction)); break;
    case "1h": d.setHours(d.getHours() + (1 * direction)); break;
    case "1d": d.setDate(d.getDate() + (1 * direction)); break;
    case "1mo": d.setMonth(d.getMonth() + (1 * direction)); break;
    case "1y": d.setFullYear(d.getFullYear() + (1 * direction)); break;
    default: d.setDate(d.getDate() + (1 * direction));
  }

  STATE.currentDateTime = d;
  fetchAndRenderCapturedHoroscope(false);
}

// ==========================================================================
// 4. AUTOMATIC GPS GEOLOCATION & REVERSE GEOCODING
// ==========================================================================

function initAutoGps(forceAlert = false) {
  const badge = document.getElementById("displayLocationSub");
  
  if (!navigator.geolocation) {
    if (forceAlert) alert("Geolocation is not supported by your browser.");
    return;
  }

  badge.innerHTML = "Detecting GPS Location...";

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      STATE.latitude = pos.coords.latitude;
      STATE.longitude = pos.coords.longitude;
      if (pos.coords.altitude) {
        STATE.altitude = pos.coords.altitude;
      }

      const clientOffsetHours = - (new Date().getTimezoneOffset() / 60);
      STATE.timeOffset = clientOffsetHours;

      try {
        const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${STATE.latitude}&lon=${STATE.longitude}&format=json`);
        if (resp.ok) {
          const data = await resp.json();
          const addr = data.address || {};
          const city = addr.city || addr.town || addr.village || addr.suburb || addr.county || "Detected Location";
          const state = addr.state || "";
          const country = addr.country || "";
          STATE.cityName = `${city}, ${state} ${addr.postcode || ''}, ${country}`.trim().replace(/,\s*,/g, ',');
        }
      } catch (err) {
        console.warn("Reverse geocode lookup failed, using coordinates:", err);
        STATE.cityName = `Lat: ${STATE.latitude.toFixed(4)}, Lon: ${STATE.longitude.toFixed(4)}`;
      }

      badge.innerHTML = `${STATE.cityName}`;
      fetchLiveHoroscope(false);
      fetchAndRenderCapturedHoroscope(false);
      if (forceAlert) alert(`Location updated: ${STATE.cityName}`);
    },
    (err) => {
      console.warn("Geolocation permission not granted or error:", err);
      badge.innerHTML = `${STATE.cityName}`;
      if (forceAlert) alert("Could not obtain GPS. Using default location.");
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

// ==========================================================================
// 5. API COMMUNICATION (LIVE & CAPTURED WITH MILLISECONDS)
// ==========================================================================

async function fetchLiveHoroscope(alsoInitCaptured = false) {
  if (STATE.isFetchingLive) return;
  STATE.isFetchingLive = true;

  const targetTime = new Date(STATE.liveDateTime);
  const payload = {
    datetime_str: formatDateTimeLocal(targetTime),
    latitude: STATE.latitude,
    longitude: STATE.longitude,
    altitude: STATE.altitude,
    is_local: true,
    time_offset: STATE.timeOffset,
    method: STATE.method.toLowerCase()
  };

  try {
    const res = await fetch("/api/horoscope", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Server returned status ${res.status}`);
    }

    const data = await res.json();
    STATE.liveHoroscopeData = data;
    renderLiveChartFromState();

    if (alsoInitCaptured || !STATE.latestHoroscopeData) {
      STATE.currentDateTime = new Date(targetTime);
      STATE.latestHoroscopeData = JSON.parse(JSON.stringify(data));
      addSnapshotToVault(STATE.latestHoroscopeData);
      renderCapturedChartFromState();
    }
  } catch (err) {
    console.error("Failed to fetch live horoscope:", err);
  } finally {
    STATE.isFetchingLive = false;
  }
}

async function fetchAndRenderCapturedHoroscope(saveToVault = false) {
  const payload = {
    datetime_str: formatDateTimeLocal(STATE.currentDateTime),
    latitude: STATE.latitude,
    longitude: STATE.longitude,
    altitude: STATE.altitude,
    is_local: true,
    time_offset: STATE.timeOffset,
    method: STATE.method.toLowerCase()
  };

  try {
    const res = await fetch("/api/horoscope", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Server returned status ${res.status}`);
    }

    const data = await res.json();
    STATE.latestHoroscopeData = data;
    if (saveToVault) {
      addSnapshotToVault(data);
    }
    renderCapturedChartFromState();
  } catch (err) {
    console.error("Failed to fetch captured horoscope:", err);
    document.getElementById("displayFormattedTime").innerText = "Error calculating horoscope: " + err.message;
  }
}

// ==========================================================================
// 6. DUAL CHART & DATA RENDERING ENGINE
// ==========================================================================

function renderLiveChartFromState() {
  const data = STATE.liveHoroscopeData;
  if (!data) return;

  const dt = new Date(STATE.liveDateTime);
  const tzFormatted = formatTzOffset(data.main_chart ? STATE.timeOffset : 5.5);
  const formattedHeaderTime = formatDateToCustomString(dt, true) + ` (${tzFormatted})`;

  // Update Hora in Header Top Bar from Live Chart
  const horaInfo = data.hora_info;
  if (horaInfo) {
    document.getElementById("headerHoraValue").innerText = `${horaInfo.hora_lord} (${horaInfo.hora_display.split('(')[1] || ''}`;
  }

  // Render Live Chart into "live-" prefixed DOM elements
  renderChartBox(data, "main", "live-", formattedHeaderTime);
}

function renderCapturedChartFromState() {
  const data = STATE.latestHoroscopeData;
  if (!data) return;

  const dt = new Date(data.datetime_local);
  const tzFormatted = formatTzOffset(data.main_chart ? STATE.timeOffset : 5.5);
  const formattedHeaderTime = formatDateToCustomString(dt, true) + ` (${tzFormatted})`;

  // Update Center Inspector & Captured Header Clock (with milliseconds)
  document.getElementById("displayFormattedTime").innerText = `${formattedHeaderTime}`;
  document.getElementById("displayLocationSub").innerText = `${STATE.cityName} (${STATE.latitude.toFixed(4)} / ${STATE.longitude.toFixed(4)})`;

  const capturedClockEl = document.getElementById("capturedHeaderClock");
  if (capturedClockEl) {
    capturedClockEl.innerText = formatDateToCustomString(dt, true);
  }

  // Sync Toolbar Inputs (if not currently focused)
  const dayInp = document.getElementById("inpDay");
  const monthInp = document.getElementById("inpMonth");
  const yearInp = document.getElementById("inpYear");
  const timeInp = document.getElementById("inpTime");
  const cityInp = document.getElementById("inpCityToolbar");

  if (dayInp && document.activeElement !== dayInp) dayInp.value = dt.getDate();
  if (monthInp && document.activeElement !== monthInp) monthInp.value = dt.getMonth();
  if (yearInp && document.activeElement !== yearInp) yearInp.value = dt.getFullYear();
  if (timeInp && document.activeElement !== timeInp) {
    const hh = String(dt.getHours()).padStart(2, '0');
    const mm = String(dt.getMinutes()).padStart(2, '0');
    const ss = String(dt.getSeconds()).padStart(2, '0');
    const ms = String(dt.getMilliseconds()).padStart(3, '0');
    timeInp.value = `${hh}:${mm}:${ss}.${ms}`;
  }
  if (cityInp && document.activeElement !== cityInp) {
    cityInp.value = STATE.cityName;
  }

  // Render Captured Chart into unprefixed DOM elements ("")
  renderChartBox(data, STATE.activeVarga, "", formattedHeaderTime);

  // Populate lower tables and print structures for Captured Chart
  renderKpTable(data);
  renderJammaPlanetsTable(data);
  updatePrintLandscapeData(data, formattedHeaderTime);
  syncPdfDocumentTitle();
  document.getElementById("ayanamsaBadge").innerText = `Lahiri Ayanamsa: ${data.ayanamsa ? formatDmsCompact(data.ayanamsa) : "24° 12' 40\""}`;
}

function renderChartBox(data, vargaKey, prefix, formattedHeaderTime) {
  const jamamInfo = data.jamam_info || { display_title: "HORA CHART" };
  const titleEl = document.getElementById(`${prefix}centerJamamTitle`);
  const timeEl = document.getElementById(`${prefix}centerTimeSubtitle`);
  const locEl = document.getElementById(`${prefix}centerLocationSubtitle`);

  if (titleEl) {
    const modeSuffix = prefix === "live-" ? " [LIVE]" : (vargaKey !== "main" ? ` [${vargaKey.toUpperCase()}]` : "");
    titleEl.innerText = `${jamamInfo.display_title}${modeSuffix}`;
  }
  if (timeEl) {
    timeEl.innerText = `${jamamInfo.day_name || 'Thursday'}, ${formattedHeaderTime}`;
  }
  if (locEl) {
    locEl.innerHTML = `${STATE.cityName}<br><span id="${prefix}centerCoords">${STATE.latitude.toFixed(5)} / ${STATE.longitude.toFixed(5)}</span>`;
  }

  // Clear all 12 Rasi cells for this chart
  for (let i = 0; i < 12; i++) {
    const pEl = document.getElementById(`${prefix}cell-planets-${i}`);
    if (pEl) pEl.innerHTML = "";
  }

  if (vargaKey === "main" || vargaKey === "d1") {
    renderMainJamakkolChart(data, prefix);
  } else {
    renderDivisionalChart(data, vargaKey, prefix);
  }
}

function renderMainJamakkolChart(data, prefix = "") {
  const main = data.main_chart;
  const p = main.planets;
  const jp = main.jamma_planets;
  const u = main.udhayam;
  const ar = main.arudham;
  const kv = main.kavippu;
  const md = main.mandi;
  const asc = main.ascendant_sidereal;

  const udhayamRasi = u.housedetails.house;

  // Set house numbers in all 12 cells (1 to 12 relative to Udhayam)
  for (let r = 0; r < 12; r++) {
    const hEl = document.getElementById(`${prefix}cell-house-${r}`);
    if (hEl) {
      if (STATE.houseIndexMode === "0to11") {
        hEl.innerText = ((r - udhayamRasi + 12) % 12);
      } else {
        hEl.innerText = ((r - udhayamRasi + 12) % 12) + 1;
      }
    }
  }

  const signBodies = Array.from({ length: 12 }, () => []);

  // 1. Special points
  if (asc) {
    signBodies[asc.housedetails.house].push({
      code: "ASC",
      deg: asc.housedetails.deg,
      deg_in_sign: asc.housedetails.deg % 30,
      cssClass: "asc-tag"
    });
  }
  if (u) {
    signBodies[u.housedetails.house].push({
      code: "UD",
      deg: u.housedetails.deg,
      deg_in_sign: u.housedetails.deg % 30,
      cssClass: "special-tag"
    });
  }
  if (ar) {
    signBodies[ar.house].push({
      code: "AR",
      deg: ar.deg,
      deg_in_sign: ar.deg % 30,
      cssClass: "special-tag"
    });
  }
  if (kv) {
    signBodies[kv.house].push({
      code: "(KV)",
      deg: kv.deg,
      deg_in_sign: kv.deg % 30,
      cssClass: "special-tag"
    });
  }
  if (md) {
    signBodies[md.house].push({
      code: "md",
      deg: md.deg,
      deg_in_sign: md.deg % 30,
      cssClass: "planet-tag"
    });
  }

  // 2. Main Ephemeris Planets
  const planetDefs = [
    { code: "SU", p: p.sun },
    { code: "MO", p: p.moon },
    { code: "MA", p: p.mars },
    { code: "ME", p: p.mercury },
    { code: "JU", p: p.jupiter },
    { code: "VE", p: p.venus },
    { code: "SA", p: p.saturn },
    { code: "RA", p: p.rahu },
    { code: "KE", p: p.ketu }
  ];

  planetDefs.forEach(item => {
    if (item.p) {
      const isRet = item.p.is_retrograde && item.code !== "RA" && item.code !== "KE";
      let label = item.code;
      if (isRet || item.code === "RA" || item.code === "KE" || item.code === "SA") {
        label = `(${item.code})`;
      }
      signBodies[item.p.housedetails.house].push({
        code: label,
        deg: item.p.housedetails.deg,
        deg_in_sign: item.p.housedetails.deg % 30,
        cssClass: "planet-tag"
      });
    }
  });

  // 3. Render each cell SORTED STRICTLY BY DEGREE IN SIGN (Ascending)
  for (let r = 0; r < 12; r++) {
    const bodies = signBodies[r];
    bodies.sort((a, b) => a.deg_in_sign - b.deg_in_sign);
    bodies.forEach(b => addChartTag(r, b.code, b.cssClass, b.deg_in_sign, prefix));
  }

  renderOuterWheelSlots(jp, prefix);
  renderCenterDegreesTable(asc, p, u, ar, kv, md, prefix);
}

function renderDivisionalChart(data, vargaKey, prefix = "") {
  const vargaChart = data.divisional_charts[vargaKey];
  if (!vargaChart) return;

  const lagnaRasi = vargaChart.ascendant.sign_index;

  for (let r = 0; r < 12; r++) {
    const hEl = document.getElementById(`${prefix}cell-house-${r}`);
    if (hEl) {
      if (STATE.houseIndexMode === "0to11") {
        hEl.innerText = ((r - lagnaRasi + 12) % 12);
      } else {
        hEl.innerText = ((r - lagnaRasi + 12) % 12) + 1;
      }
    }
  }

  const signBodies = Array.from({ length: 12 }, () => []);

  signBodies[vargaChart.ascendant.sign_index].push({
    code: "ASC",
    deg_in_sign: vargaChart.ascendant.deg_in_varga,
    cssClass: "asc-tag"
  });

  const bodies = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"];
  const codes = ["SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE"];

  bodies.forEach((bName, idx) => {
    const b = vargaChart[bName];
    if (b) {
      let label = codes[idx];
      if (codes[idx] === "RA" || codes[idx] === "KE" || codes[idx] === "SA") {
        label = `(${label})`;
      }
      signBodies[b.sign_index].push({
        code: label,
        deg_in_sign: b.deg_in_varga,
        cssClass: "planet-tag"
      });
    }
  });

  for (let r = 0; r < 12; r++) {
    const bList = signBodies[r];
    bList.sort((a, b) => a.deg_in_sign - b.deg_in_sign);
    bList.forEach(b => addChartTag(r, b.code, b.cssClass, b.deg_in_sign, prefix));
  }

  renderCenterVargaDegrees(vargaChart, prefix);
}

function addChartTag(rasiIndex, text, cssClass, degInSign, prefix = "") {
  const cell = document.getElementById(`${prefix}cell-planets-${rasiIndex}`);
  if (cell) {
    const span = document.createElement("span");
    span.className = cssClass;
    if (degInSign !== undefined && degInSign !== null) {
      const degInt = Math.floor(degInSign);
      span.innerHTML = `<span class="tag-sym">${text}</span> <span class="tag-deg">${degInt}</span>`;
    } else {
      span.innerHTML = `<span class="tag-sym">${text}</span>`;
    }
    cell.appendChild(span);
  }
}

function renderOuterWheelSlots(jp, prefix = "") {
  if (!jp) return;
  
  const getSlotText = (planetObj, arrowLeft = true) => {
    if (!planetObj) return "";
    const shortCode = PLANET_SHORT_NAMES[planetObj.planet_name] || planetObj.planet_name.substr(0,2).toUpperCase();
    const symbol = PLANET_SYMBOLS[planetObj.planet_name] || "";
    const dms = formatDmsShort(planetObj.housedetails.deg);
    const label = symbol ? `${shortCode} ${symbol}` : shortCode;
    return arrowLeft ? `← ${label} ${dms}` : `${label} ${dms} →`;
  };

  const sectorSlots = [
    { id: `${prefix}jw-top-ari`, arrowLeft: true },
    { id: `${prefix}jw-top-gem`, arrowLeft: true },
    { id: `${prefix}jw-right-can`, arrowLeft: false },
    { id: `${prefix}jw-right-vir`, arrowLeft: false },
    { id: `${prefix}jw-bottom-lib`, arrowLeft: false },
    { id: `${prefix}jw-bottom-sag`, arrowLeft: false },
    { id: `${prefix}jw-left-cap`, arrowLeft: true },
    { id: `${prefix}jw-left-pis`, arrowLeft: true }
  ];

  sectorSlots.forEach(slot => {
    const el = document.getElementById(slot.id);
    if (el) el.innerText = "";
  });

  const jNames = ["sun", "mars", "jupiter", "mercury", "venus", "saturn", "moon", "snake"];
  jNames.forEach(name => {
    const pObj = jp[name];
    if (pObj && pObj.housedetails && pObj.housedetails.deg !== undefined) {
      const deg = ((pObj.housedetails.deg % 360) + 360) % 360;
      const sectorIdx = Math.floor(deg / 45);
      if (sectorIdx >= 0 && sectorIdx < 8) {
        const slot = sectorSlots[sectorIdx];
        const el = document.getElementById(slot.id);
        if (el) {
          el.innerText = getSlotText(pObj, slot.arrowLeft);
        }
      }
    }
  });
}

function renderCenterDegreesTable(asc, p, u, ar, kv, md, prefix = "") {
  const leftCol = document.getElementById(`${prefix}degColLeft`);
  const rightCol = document.getElementById(`${prefix}degColRight`);
  if (!leftCol || !rightCol) return;
  leftCol.innerHTML = "";
  rightCol.innerHTML = "";

  const allItems = [
    { code: "ASC", deg: asc ? asc.housedetails.deg : 0 },
    { code: "SU", deg: p.sun ? p.sun.housedetails.deg : 0 },
    { code: "MO", deg: p.moon ? p.moon.housedetails.deg : 0 },
    { code: "MA", deg: p.mars ? p.mars.housedetails.deg : 0 },
    { code: "ME", deg: p.mercury ? p.mercury.housedetails.deg : 0 },
    { code: "JU", deg: p.jupiter ? p.jupiter.housedetails.deg : 0 },
    { code: "VE", deg: p.venus ? p.venus.housedetails.deg : 0 },
    { code: "SA", deg: p.saturn ? p.saturn.housedetails.deg : 0 },
    { code: "RA", deg: p.rahu ? p.rahu.housedetails.deg : 0 },
    { code: "KE", deg: p.ketu ? p.ketu.housedetails.deg : 0 },
    { code: "UD", deg: u ? u.housedetails.deg : 0 },
    { code: "AR", deg: ar ? ar.deg : 0 },
    { code: "KV", deg: kv ? kv.deg : 0 },
    { code: "md", deg: md ? md.deg : 0 }
  ];

  allItems.sort((a, b) => a.deg - b.deg);

  const itemsLeft = allItems.slice(0, 7);
  const itemsRight = allItems.slice(7, 14);

  itemsLeft.forEach(item => {
    const row = document.createElement("div");
    row.className = "deg-row";
    row.innerHTML = `<span class="code">${item.code}</span><span class="val">${formatDmsTotal(item.deg)}</span>`;
    leftCol.appendChild(row);
  });

  itemsRight.forEach(item => {
    const row = document.createElement("div");
    row.className = "deg-row";
    row.innerHTML = `<span class="code">${item.code}</span><span class="val">${formatDmsTotal(item.deg)}</span>`;
    rightCol.appendChild(row);
  });
}

function renderCenterVargaDegrees(vargaChart, prefix = "") {
  const leftCol = document.getElementById(`${prefix}degColLeft`);
  const rightCol = document.getElementById(`${prefix}degColRight`);
  if (!leftCol || !rightCol) return;
  leftCol.innerHTML = "";
  rightCol.innerHTML = "";

  const itemsLeft = [
    { code: "ASC", val: vargaChart.ascendant },
    { code: "MA", val: vargaChart.mars },
    { code: "JU", val: vargaChart.jupiter },
    { code: "ME", val: vargaChart.mercury },
    { code: "SU", val: vargaChart.sun }
  ];

  const itemsRight = [
    { code: "KE", val: vargaChart.ketu },
    { code: "VE", val: vargaChart.venus },
    { code: "MO", val: vargaChart.moon },
    { code: "RA", val: vargaChart.rahu },
    { code: "SA", val: vargaChart.saturn }
  ];

  itemsLeft.forEach(item => {
    if (item.val) {
      const row = document.createElement("div");
      row.className = "deg-row";
      row.innerHTML = `<span class="code">${item.code}</span><span class="val">${item.val.rasi.substr(0,3)} ${item.val.DMS.split(' ')[0]}</span>`;
      leftCol.appendChild(row);
    }
  });

  itemsRight.forEach(item => {
    if (item.val) {
      const row = document.createElement("div");
      row.className = "deg-row";
      row.innerHTML = `<span class="code">${item.code}</span><span class="val">${item.val.rasi.substr(0,3)} ${item.val.DMS.split(' ')[0]}</span>`;
      rightCol.appendChild(row);
    }
  });
}

function renderKpTable(data) {
  const tbody = document.getElementById("kpTableBody");
  tbody.innerHTML = "";

  const main = data.main_chart;
  const p = main.planets;
  const asc = main.ascendant_sidereal;
  const u = main.udhayam;
  const ar = main.arudham;
  const kv = main.kavippu;

  const rows = [];
  if (asc) rows.push({ name: "Ascendant (Lagna)", p: asc });
  if (u) rows.push({ name: "Udhayam Lagna", p: { housedetails: u.housedetails, is_retrograde: false } });
  if (ar) rows.push({ name: "Arudham Point", p: { housedetails: ar, is_retrograde: false } });
  if (kv) rows.push({ name: "Kavippu Point", p: { housedetails: kv, is_retrograde: false } });

  const pNames = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"];
  pNames.forEach(n => {
    if (p[n]) rows.push({ name: n.charAt(0).toUpperCase() + n.slice(1), p: p[n] });
  });

  rows.forEach(item => {
    const hd = item.p.housedetails;
    const kp = hd.kp_details || {};
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><strong>${item.name}</strong></td>
      <td>${hd.rasi || 'Mesham'}</td>
      <td>${hd.house}</td>
      <td class="mono-cell">${hd.DMS}</td>
      <td>${item.p.is_retrograde ? '<span class="badge badge-info">Retrograde (R)</span>' : 'Direct'}</td>
      <td>${kp.nakshatra_name_en || '-'} - ${kp.pada || 1}</td>
      <td>${kp.star_lord || '-'}</td>
      <td><strong>${kp.sub_lord || '-'}</strong></td>
      <td>${kp.sub_sub_lord || '-'}</td>
      <td>${kp.sub_sub_sub_lord || '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderJammaPlanetsTable(data) {
  const tbody = document.getElementById("jammaTableBody");
  tbody.innerHTML = "";

  const jp = data.main_chart.jamma_planets;
  if (!jp) return;

  const jNames = ["sun", "mars", "jupiter", "mercury", "venus", "saturn", "moon", "snake"];
  jNames.forEach(n => {
    const item = jp[n];
    if (item) {
      const hd = item.housedetails;
      const kp = hd.kp_details || {};
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${item.planet_name}</strong></td>
        <td>${hd.rasi} (${item.rasi_name_en})</td>
        <td>${hd.house}</td>
        <td class="mono-cell">${hd.DMS}</td>
        <td class="mono-cell">${item.start_deg_dms || (item.start_deg !== undefined ? formatDmsTotal(item.start_deg) : formatDmsTotal(hd.deg))}</td>
        <td>${kp.star_lord || '-'}</td>
        <td><strong>${kp.sub_lord || '-'}</strong></td>
      `;
      tbody.appendChild(tr);
    }
  });
}

// ==========================================================================
// 7. PRINT LANDSCAPE DATA UPDATE & EXPORT (WITH MILLISECOND FILENAME)
// ==========================================================================

function updatePrintLandscapeData(data, formattedTime) {
  const clientName = document.getElementById("clientNameInput").value.trim() || "Rajagopal";
  const notes = document.getElementById("clientNotesInput").value.trim() || "-";

  document.getElementById("printNameDisplay").innerText = clientName;
  document.getElementById("printDateTimeDisplay").innerText = formattedTime;
  document.getElementById("printLocDisplay").innerText = `${STATE.cityName} (${STATE.latitude.toFixed(4)} / ${STATE.longitude.toFixed(4)})`;
  
  const jamamInfo = data.jamam_info || {};
  const horaInfo = data.hora_info || {};
  document.getElementById("printJamamHoraDisplay").innerText = `${jamamInfo.day_name || 'Thursday'} Jamam #${jamamInfo.jamam_number || 4} | ${horaInfo.hora_display || ''}`;
  document.getElementById("printAyaDisplay").innerText = `Lahiri ${data.ayanamsa ? formatDmsCompact(data.ayanamsa) : ''}`;
  document.getElementById("printNotesDisplay").innerText = notes;

  const colLeft = document.getElementById("printColLeft");
  const colRight = document.getElementById("printColRight");
  colLeft.innerHTML = "";
  colRight.innerHTML = "";

  const main = data.main_chart;
  const p = main.planets;
  const asc = main.ascendant_sidereal;
  const u = main.udhayam;
  const ar = main.arudham;
  const kv = main.kavippu;
  const md = main.mandi;

  const listLeft = [
    { code: "ASC", name: "Lagna", obj: asc ? asc.housedetails : null },
    { code: "MA", name: "Mars", obj: p.mars ? p.mars.housedetails : null },
    { code: "md", name: "Mandi", obj: md },
    { code: "JU", name: "Jupiter", obj: p.jupiter ? p.jupiter.housedetails : null },
    { code: "AR", name: "Arudham", obj: ar },
    { code: "ME", name: "Mercury", obj: p.mercury ? p.mercury.housedetails : null },
    { code: "SU", name: "Sun", obj: p.sun ? p.sun.housedetails : null }
  ];

  const listRight = [
    { code: "KE", name: "Ketu", obj: p.ketu ? p.ketu.housedetails : null },
    { code: "KV", name: "Kavippu", obj: kv },
    { code: "VE", name: "Venus", obj: p.venus ? p.venus.housedetails : null },
    { code: "MO", name: "Moon", obj: p.moon ? p.moon.housedetails : null },
    { code: "UD", name: "Udhayam", obj: u ? u.housedetails : null },
    { code: "RA", name: "Rahu", obj: p.rahu ? p.rahu.housedetails : null },
    { code: "SA", name: "Saturn", obj: p.saturn ? p.saturn.housedetails : null }
  ];

  const renderPrintDegItem = (container, item) => {
    if (!item.obj) return;
    const div = document.createElement("div");
    div.className = "print-deg-item";
    const rasiShort = item.obj.rasi ? item.obj.rasi.substr(0,3) : RASI_SHORT_NAMES[Math.floor(item.obj.deg/30)];
    const degStr = item.obj.DMS ? item.obj.DMS.split(' ')[0] + ' ' + item.obj.DMS.split(' ')[1] : formatDmsShort(item.obj.deg);
    
    const kp = item.obj.kp_details || {};
    const nakName = kp.nakshatra_name_en ? `${kp.nakshatra_name_en.substr(0,7)}-${kp.pada || 1}` : '';
    const lordStr = (kp.star_lord && kp.sub_lord) ? `[${kp.star_lord.substr(0,2)}/${kp.sub_lord.substr(0,2)}]` : '';

    div.innerHTML = `
      <span class="p-code">${item.code}</span>
      <span class="p-sign">${rasiShort} (H${item.obj.house})</span>
      <span class="p-deg">${degStr}</span>
      <span class="p-nak">${nakName}</span>
      <span class="p-lord">${lordStr}</span>
    `;
    container.appendChild(div);
  };

  listLeft.forEach(item => renderPrintDegItem(colLeft, item));
  listRight.forEach(item => renderPrintDegItem(colRight, item));
}

function syncPdfDocumentTitle() {
  const clientNameEl = document.getElementById("clientNameInput");
  const clientName = (clientNameEl ? clientNameEl.value.trim() : "") || "Rajagopal";
  const chartDt = STATE.latestHoroscopeData && STATE.latestHoroscopeData.datetime_local
    ? new Date(STATE.latestHoroscopeData.datetime_local)
    : STATE.currentDateTime;
  const chartTimeStr = formatDateToCustomString(chartDt, true).replace(/:/g, "-").replace(/\s+/g, "_");
  document.title = `${clientName}_${chartTimeStr}`;
}

async function handleSavePdf() {
  if (STATE.latestHoroscopeData) {
    const dt = new Date(STATE.latestHoroscopeData.datetime_local);
    const tzFormatted = formatTzOffset(STATE.timeOffset);
    const formattedHeaderTime = formatDateToCustomString(dt, true) + ` (${tzFormatted})`;
    updatePrintLandscapeData(STATE.latestHoroscopeData, formattedHeaderTime);
  }
  syncPdfDocumentTitle();

  // If running in Electron Desktop App, use native printToPDF with Save Dialog pre-filled with exact millisecond filename
  if (window.obsidianAPI && window.obsidianAPI.isElectron) {
    try {
      await window.obsidianAPI.exportLandscapePDF(`${document.title}.pdf`);
      return;
    } catch (err) {
      console.warn("Electron printToPDF fallback to window.print():", err);
    }
  }

  window.print();
}

// ==========================================================================
// 7B. OBSIDIAN COMMAND PALETTE (Ctrl+P / Ctrl+K)
// ==========================================================================

const OBSIDIAN_COMMANDS = [
  {
    title: "⚡ Capture Exact Millisecond Moment to Right Chart & Vault",
    shortcut: "Click Chart / Space",
    action: () => captureLiveMomentToRight()
  },
  {
    title: "💾 Save Captured Chart & Notes as Markdown (.md) to Local Vault",
    shortcut: "Ctrl+S",
    action: () => saveActiveEditorMarkdownToVault()
  },
  {
    title: "📄 Export Single-Page Landscape PDF Report (with .ms filename)",
    shortcut: "Ctrl+P (Print)",
    action: () => handleSavePdf()
  },
  {
    title: "📂 Toggle Local Markdown (.md) Vault Explorer Sidebar",
    shortcut: "Ctrl+B",
    action: () => document.getElementById("btnToggleVault")?.click()
  },
  {
    title: "📝 Focus CodeMirror Consultation Markdown Editor",
    shortcut: "Ctrl+E",
    action: () => document.getElementById("btnNavEditor")?.click()
  },
  {
    title: "📊 Scroll to KP Sub-Lords & Rotational Grahas Tables",
    shortcut: "Tables",
    action: () => document.getElementById("btnNavTables")?.click()
  },
  {
    title: "🔄 Switch Captured Chart to Hora (Main Jamakkol Chart)",
    shortcut: "Varga: Hora",
    action: () => selectVargaProgrammatically("main")
  },
  {
    title: "🔄 Switch Captured Chart to D-9 Navamsha (Marriage / Dharma)",
    shortcut: "Varga: D-9",
    action: () => selectVargaProgrammatically("d9")
  },
  {
    title: "🔄 Switch Captured Chart to D-10 Dasamsha (Career & Fame)",
    shortcut: "Varga: D-10",
    action: () => selectVargaProgrammatically("d10")
  },
  {
    title: "🔄 Switch Captured Chart to D-60 Shashtiamsha (Root Karma)",
    shortcut: "Varga: D-60",
    action: () => selectVargaProgrammatically("d60")
  },
  {
    title: "🎨 Toggle Chart Grid Theme (Classic Cream vs. Obsidian Dark)",
    shortcut: "Chart Theme",
    action: () => document.getElementById("btnToggleChartTheme")?.click()
  },
  {
    title: "🌗 Toggle Workspace Theme (Obsidian Dark vs. Light)",
    shortcut: "App Theme",
    action: () => document.getElementById("btnToggleAppTheme")?.click()
  },
  {
    title: "⚙️ Open Horoscope & Location Settings",
    shortcut: "Settings",
    action: () => document.getElementById("btnSettings")?.click()
  }
];

function selectVargaProgrammatically(vargaKey) {
  STATE.activeVarga = vargaKey;
  const sel = document.getElementById("allVargasSelect");
  if (sel) sel.value = vargaKey;
  document.querySelectorAll(".view-tab").forEach((t) => {
    t.classList.toggle("active", t.getAttribute("data-varga") === vargaKey);
  });
  updateCapturedVargaBadge();
  renderCapturedChartFromState();
}

function setupCommandPalette() {
  const modal = document.getElementById("commandPaletteModal");
  const input = document.getElementById("cmdPaletteInput");
  const listEl = document.getElementById("cmdPaletteList");
  const btnRibbonCmd = document.getElementById("btnCommandPalette");
  const btnTopCmd = document.getElementById("btnTopCmdPalette");

  if (!modal || !input || !listEl) return;

  let filteredCommands = [...OBSIDIAN_COMMANDS];

  const renderCmdList = () => {
    const q = (input.value || "").trim().toLowerCase();
    filteredCommands = OBSIDIAN_COMMANDS.filter((c) => c.title.toLowerCase().includes(q) || c.shortcut.toLowerCase().includes(q));
    if (STATE.cmdSelectedIndex >= filteredCommands.length) {
      STATE.cmdSelectedIndex = 0;
    }
    listEl.innerHTML = "";
    filteredCommands.forEach((cmd, idx) => {
      const item = document.createElement("div");
      item.className = `cmd-item${idx === STATE.cmdSelectedIndex ? " selected" : ""}`;
      item.innerHTML = `
        <span>${cmd.title}</span>
        <span class="cmd-shortcut">${cmd.shortcut}</span>
      `;
      item.addEventListener("click", () => {
        modal.classList.remove("open");
        cmd.action();
      });
      listEl.appendChild(item);
    });
  };

  const openCmdPalette = () => {
    input.value = "";
    STATE.cmdSelectedIndex = 0;
    renderCmdList();
    modal.classList.add("open");
    setTimeout(() => input.focus(), 20);
  };

  if (btnRibbonCmd) btnRibbonCmd.addEventListener("click", openCmdPalette);
  if (btnTopCmd) btnTopCmd.addEventListener("click", openCmdPalette);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.remove("open");
  });

  input.addEventListener("input", () => {
    STATE.cmdSelectedIndex = 0;
    renderCmdList();
  });

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === "k" || e.key.toLowerCase() === "p")) {
      e.preventDefault();
      openCmdPalette();
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      saveActiveEditorMarkdownToVault();
      return;
    }
    if (!modal.classList.contains("open")) return;

    if (e.key === "Escape") {
      modal.classList.remove("open");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (filteredCommands.length > 0) {
        STATE.cmdSelectedIndex = (STATE.cmdSelectedIndex + 1) % filteredCommands.length;
        renderCmdList();
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (filteredCommands.length > 0) {
        STATE.cmdSelectedIndex = (STATE.cmdSelectedIndex - 1 + filteredCommands.length) % filteredCommands.length;
        renderCmdList();
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      const chosen = filteredCommands[STATE.cmdSelectedIndex];
      if (chosen) {
        modal.classList.remove("open");
        chosen.action();
      }
    }
  });
}

// ==========================================================================
// 8. HELPER FORMATTING FUNCTIONS (WITH MILLISECOND .mmm SUPPORT)
// ==========================================================================

function formatDmsTotal(deg) {
  deg = deg % 360;
  if (deg < 0) deg += 360;
  const d = Math.floor(deg);
  const mDec = (deg - d) * 60;
  const m = Math.floor(mDec);
  const s = Math.floor((mDec - m) * 60);
  return `${String(d).padStart(3, '0')}° ${String(m).padStart(2, '0')}' ${String(s).padStart(2, '0')}`;
}

function formatDmsShort(deg) {
  deg = deg % 360;
  if (deg < 0) deg += 360;
  const d = Math.floor(deg);
  const mDec = (deg - d) * 60;
  const m = Math.floor(mDec);
  return `${d}° ${String(m).padStart(2, '0')}'`;
}

function formatDmsCompact(deg) {
  const d = Math.floor(deg);
  const mDec = (deg - d) * 60;
  const m = Math.floor(mDec);
  const s = Math.round((mDec - m) * 60);
  return `${d}° ${m}' ${s}"`;
}

function formatDateToCustomString(d, includeMs = true) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const day = String(d.getDate()).padStart(2, '0');
  const month = months[d.getMonth()];
  const year = d.getFullYear();
  
  let hours = d.getHours();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  const mins = String(d.getMinutes()).padStart(2, '0');
  const secs = String(d.getSeconds()).padStart(2, '0');
  const ms = String(d.getMilliseconds()).padStart(3, '0');
  
  if (includeMs) {
    return `${day}-${month}-${year} ${String(hours).padStart(2, '0')}:${mins}:${secs}.${ms} ${ampm}`;
  }
  return `${day}-${month}-${year} ${String(hours).padStart(2, '0')}:${mins}:${secs} ${ampm}`;
}

function formatTzOffset(hours) {
  const sign = hours >= 0 ? '+' : '-';
  const absH = Math.abs(hours);
  const h = Math.floor(absH);
  const m = Math.round((absH - h) * 60);
  return `UTC${sign}${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

function formatDateTimeLocal(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const h = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  const sec = String(d.getSeconds()).padStart(2, '0');
  const ms = String(d.getMilliseconds()).padStart(3, '0');
  return `${y}-${m}-${day}T${h}:${min}:${sec}.${ms}`;
}
