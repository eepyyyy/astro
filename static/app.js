// ==========================================================================
// HORA CHART - CLIENT APPLICATION CONTROLLER
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

const STATE = {
  currentDateTime: new Date(),
  latitude: 12.98117,
  longitude: 77.48509,
  altitude: 820.0,
  cityName: "Bedarahalli, Bengaluru, Karnataka 560091",
  timeOffset: 5.5,
  method: "vedic",
  activeVarga: "main",
  houseIndexMode: "0to11", // '0to11' or '1to12'
  latestHoroscopeData: null,
  clientName: "Rajagopal",
  clientNotes: ""
};

// ==========================================================================
// 1. INITIALIZATION & LIFECYCLE
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  initAutoGps();
  fetchAndRenderHoroscope();
});

function setupEventListeners() {
  // Navigation step buttons
  document.getElementById("btnStepPrev").addEventListener("click", () => stepTime(-1));
  document.getElementById("btnStepNext").addEventListener("click", () => stepTime(1));
  document.getElementById("btnNow").addEventListener("click", () => {
    STATE.currentDateTime = new Date();
    fetchAndRenderHoroscope();
  });

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
      fetchAndRenderHoroscope();
    }
  });

  // Settings Modal
  const modal = document.getElementById("settingsModal");
  document.getElementById("btnSettings").addEventListener("click", () => {
    document.getElementById("cfgCityName").value = STATE.cityName;
    document.getElementById("cfgLat").value = STATE.latitude;
    document.getElementById("cfgLon").value = STATE.longitude;
    document.getElementById("cfgAlt").value = STATE.altitude;
    document.getElementById("cfgTz").value = STATE.timeOffset;
    document.getElementById("cfgMethod").value = STATE.method;
    document.getElementById("cfgHouseIndexMode").value = STATE.houseIndexMode;
    modal.classList.add("open");
  });

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
    fetchAndRenderHoroscope();
  });

  // Save / Export PDF Buttons
  const btnSavePdf = document.getElementById("btnSavePdf");
  if (btnSavePdf) btnSavePdf.addEventListener("click", handleSavePdf);

  const btnToolbarPdf = document.getElementById("btnToolbarPdf");
  if (btnToolbarPdf) btnToolbarPdf.addEventListener("click", handleSavePdf);

  // Direct Date & Time Toolbar Inputs
  const handleToolbarDateChange = () => {
    const day = parseInt(document.getElementById("inpDay").value) || 1;
    const month = parseInt(document.getElementById("inpMonth").value) || 0;
    const year = parseInt(document.getElementById("inpYear").value) || 2026;
    const timeVal = document.getElementById("inpTime").value || "00:00:00";
    const parts = timeVal.split(':').map(n => parseInt(n) || 0);
    const hh = parts[0] || 0;
    const mm = parts[1] || 0;
    const ss = parts[2] || 0;

    const d = new Date(year, month, day, hh, mm, ss);
    STATE.currentDateTime = d;
    fetchAndRenderHoroscope();
  };

  ["inpDay", "inpMonth", "inpYear", "inpTime"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", handleToolbarDateChange);
  });

  const cityToolbarInp = document.getElementById("inpCityToolbar");
  if (cityToolbarInp) {
    cityToolbarInp.addEventListener("change", (e) => {
      STATE.cityName = e.target.value.trim();
      fetchAndRenderHoroscope();
    });
    cityToolbarInp.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        STATE.cityName = e.target.value.trim();
        cityToolbarInp.blur();
        fetchAndRenderHoroscope();
      }
    });
  }

  // View tabs
  document.querySelectorAll(".view-tab").forEach(tab => {
    tab.addEventListener("click", (e) => {
      document.querySelectorAll(".view-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      STATE.activeVarga = tab.getAttribute("data-varga");
      document.getElementById("allVargasSelect").value = STATE.activeVarga;
      renderChartFromState();
    });
  });

  // Varga dropdown
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
    renderChartFromState();
  });
}

// ==========================================================================
// 2. TIME STEPPING ENGINE
// ==========================================================================

function stepTime(direction) {
  const unit = document.getElementById("stepUnit").value;
  const d = new Date(STATE.currentDateTime);

  switch (unit) {
    case "1m": d.setMinutes(d.getMinutes() + (1 * direction)); break;
    case "5m": d.setMinutes(d.getMinutes() + (5 * direction)); break;
    case "15m": d.setMinutes(d.getMinutes() + (15 * direction)); break;
    case "1j": d.setMinutes(d.getMinutes() + (90 * direction)); break; // 1 Jamam = 90 mins
    case "1h": d.setHours(d.getHours() + (1 * direction)); break;
    case "1d": d.setDate(d.getDate() + (1 * direction)); break;
    case "1mo": d.setMonth(d.getMonth() + (1 * direction)); break;
    case "1y": d.setFullYear(d.getFullYear() + (1 * direction)); break;
    default: d.setDate(d.getDate() + (1 * direction));
  }

  STATE.currentDateTime = d;
  fetchAndRenderHoroscope();
}

// ==========================================================================
// 3. AUTOMATIC GPS GEOLOCATION & REVERSE GEOCODING
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

      // Auto-detect timezone offset
      const clientOffsetHours = - (new Date().getTimezoneOffset() / 60);
      STATE.timeOffset = clientOffsetHours;

      // Reverse geocode via OpenStreetMap Nominatim
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
      fetchAndRenderHoroscope();
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
// 4. API COMMUNICATION
// ==========================================================================

async function fetchAndRenderHoroscope() {
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
    renderChartFromState();
  } catch (err) {
    console.error("Failed to fetch horoscope:", err);
    document.getElementById("displayFormattedTime").innerText = "Error calculating horoscope: " + err.message;
  }
}

// ==========================================================================
// 5. CHART & DATA RENDERING ENGINE
// ==========================================================================

function renderChartFromState() {
  const data = STATE.latestHoroscopeData;
  if (!data) return;

  const dt = new Date(data.datetime_local);
  
  // Format active timestamp header
  const tzFormatted = formatTzOffset(data.main_chart ? STATE.timeOffset : 5.5);
  const formattedHeaderTime = formatDateToCustomString(dt) + ` (${tzFormatted})`;
  document.getElementById("displayFormattedTime").innerText = formattedHeaderTime;
  document.getElementById("displayLocationSub").innerText = `${STATE.cityName} (${STATE.latitude.toFixed(5)} / ${STATE.longitude.toFixed(5)})`;

  // Update Hora in Header Top Bar
  const horaInfo = data.hora_info;
  if (horaInfo) {
    document.getElementById("headerHoraValue").innerText = `${horaInfo.hora_lord} (${horaInfo.hora_display.split('(')[1] || ''}`;
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
    timeInp.value = `${hh}:${mm}:${ss}`;
  }
  if (cityInp && document.activeElement !== cityInp) {
    cityInp.value = STATE.cityName;
  }

  // Center Box Content (Title set to HORA CHART)
  const jamamInfo = data.jamam_info || { display_title: "HORA CHART" };
  document.getElementById("centerJamamTitle").innerText = jamamInfo.display_title;
  document.getElementById("centerTimeSubtitle").innerText = `${jamamInfo.day_name || 'Thursday'}, ${formattedHeaderTime}`;
  document.getElementById("centerLocationSubtitle").innerHTML = `${STATE.cityName}<br><span id="centerCoords">${STATE.latitude.toFixed(5)} / ${STATE.longitude.toFixed(5)}</span>`;

  // Clear all 12 Rasi cells
  for (let i = 0; i < 12; i++) {
    const pEl = document.getElementById(`cell-planets-${i}`);
    if (pEl) pEl.innerHTML = "";
  }

  // Determine whether we are rendering Main Chart or a Divisional Chart
  if (STATE.activeVarga === "main" || STATE.activeVarga === "d1") {
    renderMainJamakkolChart(data);
  } else {
    renderDivisionalChart(data, STATE.activeVarga);
  }

  // Populate lower tables and print structures
  renderKpTable(data);
  renderJammaPlanetsTable(data);
  updatePrintLandscapeData(data, formattedHeaderTime);
  document.getElementById("ayanamsaBadge").innerText = `Lahiri Ayanamsa: ${data.ayanamsa ? formatDmsCompact(data.ayanamsa) : "24° 12' 40\""}`;
}

function renderMainJamakkolChart(data) {
  const main = data.main_chart;
  const p = main.planets;
  const jp = main.jamma_planets;
  const u = main.udhayam;
  const ar = main.arudham;
  const kv = main.kavippu;
  const md = main.mandi;
  const asc = main.ascendant_sidereal;

  const lagnaRasi = asc ? asc.housedetails.house : 0;
  const udhayamRasi = u.housedetails.house;

  // Set house numbers in all 12 cells
  for (let r = 0; r < 12; r++) {
    const hEl = document.getElementById(`cell-house-${r}`);
    if (hEl) {
      if (STATE.houseIndexMode === "0to11") {
        hEl.innerText = ((r - lagnaRasi + 12) % 12);
      } else {
        hEl.innerText = ((r - udhayamRasi + 12) % 12) + 1;
      }
    }
  }

  // Collect ALL bodies per sign to SORT THEM ACCORDING TO DEGREE IN SIGN (Ascending)
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
    bodies.forEach(b => addChartTag(r, b.code, b.cssClass));
  }

  // Render Outer Planets in border slots using short names (excluding J.)
  renderOuterWheelSlots(jp);

  // Render 2-Column Degrees in Center Box (Sorted by degree)
  renderCenterDegreesTable(asc, p, u, ar, kv, md);
}

function renderDivisionalChart(data, vargaKey) {
  const vargaChart = data.divisional_charts[vargaKey];
  if (!vargaChart) return;

  const lagnaRasi = vargaChart.ascendant.sign_index;

  // Set house numbers relative to Lagna in this Varga
  for (let r = 0; r < 12; r++) {
    const hEl = document.getElementById(`cell-house-${r}`);
    if (hEl) {
      if (STATE.houseIndexMode === "0to11") {
        hEl.innerText = ((r - lagnaRasi + 12) % 12);
      } else {
        hEl.innerText = ((r - lagnaRasi + 12) % 12) + 1;
      }
    }
  }

  const signBodies = Array.from({ length: 12 }, () => []);

  // Add Lagna
  signBodies[vargaChart.ascendant.sign_index].push({
    code: "ASC",
    deg_in_sign: vargaChart.ascendant.deg_in_varga,
    cssClass: "asc-tag"
  });

  // Add Planets
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

  // Render sorted by degree
  for (let r = 0; r < 12; r++) {
    const bList = signBodies[r];
    bList.sort((a, b) => a.deg_in_sign - b.deg_in_sign);
    bList.forEach(b => addChartTag(r, b.code, b.cssClass));
  }

  // Render Varga degrees in center
  renderCenterVargaDegrees(vargaChart);
}

function addChartTag(rasiIndex, text, cssClass) {
  const cell = document.getElementById(`cell-planets-${rasiIndex}`);
  if (cell) {
    const span = document.createElement("span");
    span.className = cssClass;
    span.innerText = text;
    cell.appendChild(span);
  }
}

function renderOuterWheelSlots(jp) {
  if (!jp) return;
  // Outer 8 rotational planets: short name (MO, SA, VE, ME, MA, JU, SU, SN) excluding 'J.'
  const getSlotText = (planetObj, arrowLeft = true) => {
    if (!planetObj) return "";
    const shortCode = PLANET_SHORT_NAMES[planetObj.planet_name] || planetObj.planet_name.substr(0,2).toUpperCase();
    const dms = formatDmsShort(planetObj.housedetails.deg);
    return arrowLeft ? `← ${shortCode} ${dms}` : `${shortCode} ${dms} →`;
  };

  // Top slots
  document.getElementById("jw-top-1").innerText = getSlotText(jp.moon, true);
  document.getElementById("jw-top-2").innerText = getSlotText(jp.saturn, true);

  // Right slots
  document.getElementById("jw-right-1").innerText = getSlotText(jp.venus, false);
  document.getElementById("jw-right-2").innerText = getSlotText(jp.mercury, false);

  // Bottom slots
  document.getElementById("jw-bottom-1").innerText = getSlotText(jp.mars, false);
  document.getElementById("jw-bottom-2").innerText = getSlotText(jp.jupiter, false);

  // Left slots
  document.getElementById("jw-left-1").innerText = getSlotText(jp.snake, true);
  document.getElementById("jw-left-2").innerText = getSlotText(jp.sun, true);
}

function renderCenterDegreesTable(asc, p, u, ar, kv, md) {
  const leftCol = document.getElementById("degColLeft");
  const rightCol = document.getElementById("degColRight");
  leftCol.innerHTML = "";
  rightCol.innerHTML = "";

  const itemsLeft = [
    { code: "ASC", deg: asc ? asc.housedetails.deg : 0 },
    { code: "MA", deg: p.mars ? p.mars.housedetails.deg : 0 },
    { code: "md", deg: md ? md.deg : 0 },
    { code: "JU", deg: p.jupiter ? p.jupiter.housedetails.deg : 0 },
    { code: "AR", deg: ar ? ar.deg : 0 },
    { code: "ME", deg: p.mercury ? p.mercury.housedetails.deg : 0 },
    { code: "SU", deg: p.sun ? p.sun.housedetails.deg : 0 }
  ];

  const itemsRight = [
    { code: "KE", deg: p.ketu ? p.ketu.housedetails.deg : 0 },
    { code: "KV", deg: kv ? kv.deg : 0 },
    { code: "VE", deg: p.venus ? p.venus.housedetails.deg : 0 },
    { code: "MO", deg: p.moon ? p.moon.housedetails.deg : 0 },
    { code: "UD", deg: u ? u.housedetails.deg : 0 },
    { code: "RA", deg: p.rahu ? p.rahu.housedetails.deg : 0 },
    { code: "SA", deg: p.saturn ? p.saturn.housedetails.deg : 0 }
  ];

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

function renderCenterVargaDegrees(vargaChart) {
  const leftCol = document.getElementById("degColLeft");
  const rightCol = document.getElementById("degColRight");
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
        <td class="mono-cell">${formatDmsTotal(hd.deg)}</td>
        <td>${kp.star_lord || '-'}</td>
        <td><strong>${kp.sub_lord || '-'}</strong></td>
      `;
      tbody.appendChild(tr);
    }
  });
}

// ==========================================================================
// 6. PRINT LANDSCAPE DATA UPDATE & EXPORT
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

  // Populate 2-Column Degrees Box in Print Panel with rich details (no blank spaces)
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
    
    // Nakshatra and Sub-Lord info with clean formatting
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

function handleSavePdf() {
  const clientName = document.getElementById("clientNameInput").value.trim() || "Rajagopal";
  const notes = document.getElementById("clientNotesInput").value.trim();
  const dateStr = formatDateToCustomString(STATE.currentDateTime).replace(/[: ]/g, "_");
  
  // Set clean document title for the PDF export
  const originalTitle = document.title;
  document.title = `${clientName}_Hora_Chart_${dateStr}`;

  // Update print data before opening print dialog
  if (STATE.latestHoroscopeData) {
    const dt = new Date(STATE.latestHoroscopeData.datetime_local);
    const tzFormatted = formatTzOffset(STATE.timeOffset);
    const formattedHeaderTime = formatDateToCustomString(dt) + ` (${tzFormatted})`;
    updatePrintLandscapeData(STATE.latestHoroscopeData, formattedHeaderTime);
  }

  window.print();

  // Restore title after print dialog closes
  setTimeout(() => {
    document.title = originalTitle;
  }, 1000);
}

// ==========================================================================
// 7. HELPER FORMATTING FUNCTIONS
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

function formatDateToCustomString(d) {
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
  return `${y}-${m}-${day}T${h}:${min}`;
}
