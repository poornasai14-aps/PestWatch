/* PestWatch frontend — auth + capture + live outbreak map + role-based views. */
const API = "";
const DEMO_CENTER = [16.3067, 80.4365]; // Guntur, AP

let map = null, layers = {}, lastFile = null;
let token = localStorage.getItem("pw_token") || "";
let me = null;
let lastDetection = null;

/* called by i18n.js when the user flips the language toggle */
function onLangChange() {
  if (!me) return;
  applyRole();
  refreshDashboard(false);
  if (lastDetection) renderDetection(lastDetection);
}

/* ---------------------------------------------------------------- helpers */
const $ = (id) => document.getElementById(id);
function toast(msg, ms = 2600) {
  const t = $("toast"); t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(t._t); t._t = setTimeout(() => t.classList.add("hidden"), ms);
}
async function authFetch(url, opts = {}) {
  opts.headers = Object.assign({}, opts.headers, token ? { Authorization: "Bearer " + token } : {});
  const r = await fetch(API + url, opts);
  if (r.status === 401) { doLogout(); throw new Error("session expired"); }
  return r;
}
async function jget(url) { return (await authFetch(url)).json(); }

/* ================================================================= AUTH */
function bindAuth() {
  document.querySelectorAll(".auth-tab").forEach((tab) =>
    tab.addEventListener("click", () => switchAuthTab(tab.dataset.tab)));

  $("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    await login($("li-user").value.trim(), $("li-pass").value);
  });

  document.querySelectorAll(".chip-cred").forEach((c) =>
    c.addEventListener("click", () => {
      $("li-user").value = c.dataset.u; $("li-pass").value = c.dataset.p;
      login(c.dataset.u, c.dataset.p);
    }));

  $("form-signup").addEventListener("submit", signup);
}

function switchAuthTab(name) {
  document.querySelectorAll(".auth-tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.tab === name));
  $("form-login").classList.toggle("hidden", name !== "login");
  $("form-signup").classList.toggle("hidden", name !== "signup");
}

async function login(username, password) {
  $("li-err").textContent = "";
  try {
    const fd = new FormData(); fd.append("username", username); fd.append("password", password);
    const r = await fetch(API + "/api/auth/login", { method: "POST", body: fd });
    const d = await r.json();
    if (!r.ok) { $("li-err").textContent = d.detail || "login failed"; return; }
    token = d.token; localStorage.setItem("pw_token", token);
    await enterApp();
  } catch (e) { $("li-err").textContent = e.message; }
}

async function signup(e) {
  e.preventDefault();
  $("su-err").textContent = "";
  const fd = new FormData();
  fd.append("username", $("su-user").value.trim());
  fd.append("password", $("su-pass").value);
  fd.append("full_name", $("su-name").value);
  fd.append("phone", $("su-phone").value);
  fd.append("farm_name", $("su-farm").value);
  fd.append("crop", $("su-crop").value);
  fd.append("lat", $("su-lat").value);
  fd.append("lon", $("su-lon").value);
  const r = await fetch(API + "/api/auth/register", { method: "POST", body: fd });
  const d = await r.json();
  if (!r.ok) { $("su-err").textContent = d.detail || "sign-up failed"; return; }
  token = d.token; localStorage.setItem("pw_token", token);
  toast("Account created — welcome!");
  await enterApp();
}

function doLogout() {
  authFetch("/api/auth/logout", { method: "POST" }).catch(() => {});
  token = ""; me = null; localStorage.removeItem("pw_token");
  $("app").classList.add("hidden");
  $("auth").classList.remove("hidden");
}

/* ================================================= enter app after login */
async function enterApp() {
  try {
    me = await jget("/api/auth/me");
  } catch { doLogout(); return; }

  $("auth").classList.add("hidden");
  $("app").classList.remove("hidden");
  applyRole();

  if (!map) { initMap(); bindCapture(); bindControls(); await loadSpeciesOptions(); }
  await refreshHealth();
  await refreshDashboard(true);
}

function applyRole() {
  const officer = me.role === "officer";
  // role tag + chip
  const tag = $("role-tag"); tag.textContent = me.role;
  tag.className = "role-tag " + me.role;
  $("user-chip").textContent = `${me.full_name}`;
  $("sub-tagline").textContent = officer ? t("tagline_officer") : t("tagline_farmer");
  $("right-title").textContent = officer ? t("step3") : t("step3_farm");
  $("alerts-title").textContent = officer ? t("alerts_all") : t("warnings_for_you");

  document.querySelectorAll(".officer-only")
    .forEach((el) => el.classList.toggle("hidden", !officer));

  // farmer: prefill capture location with their farm
  if (!officer && me.farm) {
    $("lat").value = (+me.farm.lat).toFixed(4);
    $("lon").value = (+me.farm.lon).toFixed(4);
    $("farm_name").value = me.farm.name;
  }
}

/* ------------------------------------------------------------------- map */
function initMap() {
  map = L.map("map", { zoomControl: true }).setView(DEMO_CENTER, 12);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "© OpenStreetMap © CARTO", maxZoom: 19,
  }).addTo(map);
  layers.reports = L.layerGroup().addTo(map);
  layers.clusters = L.layerGroup().addTo(map);
  layers.rings = L.layerGroup().addTo(map);
  layers.farms = L.layerGroup().addTo(map);
}
function clearLayers() { Object.values(layers).forEach((l) => l.clearLayers()); }

/* --------------------------------------------------------- detector badge */
async function refreshHealth() {
  const h = await jget("/api/health");
  const b = $("detector-badge");
  b.textContent = "detector: " + h.detector_mode;
  b.classList.toggle("live", h.detector_mode.startsWith("yolo"));
  b.classList.toggle("sim", h.detector_mode === "simulated");
}

async function loadSpeciesOptions() {
  const list = await jget("/api/species");
  const sel = $("hint_species");
  list.forEach((s) => {
    const o = document.createElement("option");
    o.value = s.key; o.textContent = s.label; sel.appendChild(o);
  });
}

/* ------------------------------------------------------- capture & detect */
function bindCapture() {
  const drop = $("drop"), fileInput = $("file");
  drop.addEventListener("click", () => fileInput.click());
  ["dragover", "dragenter"].forEach((e) =>
    drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("drag"); }));
  ["dragleave", "drop"].forEach((e) =>
    drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("drag"); }));
  drop.addEventListener("drop", (ev) => {
    if (ev.dataTransfer.files[0]) { lastFile = ev.dataTransfer.files[0]; showPreview(); }
  });
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) { lastFile = fileInput.files[0]; showPreview(); }
  });
  $("btn-detect").addEventListener("click", detect);
  $("btn-pick").addEventListener("click", randomSpot);
  $("btn-reset").addEventListener("click", resetDemo);
  $("btn-logout").addEventListener("click", doLogout);
  $("btn-manage").addEventListener("click", openManage);
  $("manage-close").addEventListener("click", () => $("manage").classList.add("hidden"));
  $("manage").addEventListener("click", (e) => { if (e.target.id === "manage") $("manage").classList.add("hidden"); });
  $("form-farm").addEventListener("submit", addFarm);
}

/* ------------------------------------------------------- officer: manage */
async function openManage() {
  $("manage").classList.remove("hidden");
  await loadManage();
}

async function loadManage() {
  const [farmsData, usersData, ob] = await Promise.all([
    jget("/api/farms"), jget("/api/users"),
    jget("/api/outbreaks?window_days=7").catch(() => ({ alerts: [] })),
  ]);
  const atRisk = new Set((ob.alerts || []).map((a) => a.farm));

  $("farm-count").textContent = farmsData.farms.length;
  $("farm-list").innerHTML = farmsData.farms.map((f) => `
    <div class="mrow">
      <div><div class="m-main">${f.name}</div>
        <div class="m-sub">${f.crop || "—"} · ${(+f.lat).toFixed(3)}, ${(+f.lon).toFixed(3)} · ${f.phone || ""}</div></div>
      ${atRisk.has(f.name) ? `<span class="m-badge risk">at risk</span>` : ``}
    </div>`).join("") || `<p class="muted">No farms yet.</p>`;

  $("user-count").textContent = usersData.users.length;
  $("user-list").innerHTML = usersData.users.map((u) => `
    <div class="mrow">
      <div><div class="m-main">${u.full_name || u.username}</div>
        <div class="m-sub">@${u.username} ${u.phone || ""}</div></div>
      <span class="m-badge ${u.role}">${u.role}</span>
    </div>`).join("");
}

async function addFarm(e) {
  e.preventDefault();
  $("mf-err").textContent = "";
  const fd = new FormData();
  fd.append("name", $("mf-name").value);
  fd.append("crop", $("mf-crop").value);
  fd.append("phone", $("mf-phone").value);
  fd.append("lat", $("mf-lat").value);
  fd.append("lon", $("mf-lon").value);
  const r = await authFetch("/api/farms", { method: "POST", body: fd });
  const d = await r.json();
  if (!r.ok) { $("mf-err").textContent = d.detail || "failed"; return; }
  toast(`Farm "${$("mf-name").value}" registered.`);
  $("form-farm").reset();
  await loadManage();
  await refreshDashboard(false);
}

function showPreview() { $("drop-label").textContent = lastFile.name; }

function randomSpot() {
  const c = (me && me.farm) ? [me.farm.lat, me.farm.lon] : DEMO_CENTER;
  $("lat").value = (c[0] + (Math.random() - 0.5) * 0.14).toFixed(4);
  $("lon").value = (c[1] + (Math.random() - 0.5) * 0.14).toFixed(4);
  toast("Picked a nearby field location.");
}

async function detect() {
  if (!lastFile) { toast("Choose a photo first."); return; }
  const btn = $("btn-detect"); btn.disabled = true; btn.textContent = "Detecting…";
  try {
    const fd = new FormData();
    fd.append("file", lastFile);
    fd.append("lat", $("lat").value);
    fd.append("lon", $("lon").value);
    fd.append("farm_name", $("farm_name").value);
    fd.append("hint_species", $("hint_species").value);
    fd.append("save", "true");
    fd.append("lang", (typeof LANG !== "undefined" ? LANG : "en"));
    const r = await authFetch("/api/detect", { method: "POST", body: fd });
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "detect failed");
    lastDetection = res;
    renderDetection(res);
    toast(res.saved ? `Detected ${res.top_label} — added to outbreak map`
                    : `No pest found (healthy)`);
    await refreshDashboard(false);
  } catch (e) { toast("Error: " + e.message); }
  finally { btn.disabled = false; btn.textContent = "Detect & Report"; }
}

function renderDetection(res) {
  $("detect-result").classList.remove("hidden");
  const wrap = document.querySelector(".canvas-wrap");

  if (res.annotated_image) {
    // VIDEO: server already drew boxes on the best frame — show it directly.
    wrap.innerHTML = `<img src="${res.annotated_image}" style="width:100%;display:block" alt="annotated frame" />`;
  } else {
    // IMAGE: draw boxes on a canvas over the uploaded photo.
    wrap.innerHTML = `<canvas id="canvas"></canvas>`;
    const canvas = $("canvas"), ctx = canvas.getContext("2d");
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width; canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      ctx.lineWidth = Math.max(2, img.width / 250);
      ctx.font = `${Math.max(14, img.width / 45)}px Segoe UI`;
      res.detections.forEach((d) => {
        const [x1, y1, x2, y2] = d.bbox;
        ctx.strokeStyle = res.species_info.color || "#e63946";
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        const tag = `${d.label} ${(d.confidence * 100).toFixed(0)}%`;
        ctx.fillStyle = res.species_info.color || "#e63946";
        const tw = ctx.measureText(tag).width + 10;
        ctx.fillRect(x1, y1 - 22, tw, 22);
        ctx.fillStyle = "#fff"; ctx.fillText(tag, x1 + 5, y1 - 5);
      });
    };
    img.src = URL.createObjectURL(lastFile);
  }
  const s = res.species_info;

  // --- Pest result block ---
  let html = `
    <div class="res-block">
      <div class="res-title">${t("pest_check")}</div>
      <div class="det-chip"><b>${res.top_label}</b></div>
      <div class="det-chip">${t("confidence")} ${(res.top_confidence * 100).toFixed(0)}%</div>
      <div class="det-chip">${res.instance_count} ${t("instances")}</div>
      <div class="det-chip">${t("mode")}: ${res.mode}</div>
      ${res.input_type === "video" ? `<div class="det-chip">🎞️ ${res.frames_processed} ${t("frames")}</div>` : ""}
      <p class="muted" style="margin:6px 0 0">${s.inspect}</p>
    </div>`;

  // --- Disease result block (second model) ---
  const d = res.disease;
  if (d && d.available) {
    const bad = !d.healthy;
    html += `
      <div class="res-block ${bad ? "res-bad" : "res-good"}">
        <div class="res-title">${t("disease_check")}</div>
        <div class="det-chip" style="border-color:${d.color}">
          <b>${bad ? "⚠ " : "✅ "}${d.top_label}</b></div>
        <div class="det-chip">${t("confidence")} ${(d.confidence * 100).toFixed(0)}%</div>
        <p class="muted" style="margin:6px 0 2px">${d.note}</p>
        ${bad ? `<p style="margin:2px 0 0"><b style="color:#22c55e">${t("action")}:</b> ${d.action}</p>` : ""}
      </div>`;
  } else {
    html += `<div class="res-block"><div class="res-title">${t("disease_check")}</div>
      <p class="muted" style="margin:4px 0 0">${t("disease_not_installed")}</p></div>`;
  }
  $("detect-meta").innerHTML = html;
}

/* --------------------------------------------------- dashboard (map+alerts) */
function params() {
  return { eps: +$("eps").value, min: +$("minpts").value, win: +$("window").value };
}

async function refreshDashboard(fit = false) {
  const p = params();
  const lng = (typeof LANG !== "undefined" ? LANG : "en");
  const [geo, data, farmsData] = await Promise.all([
    jget(`/api/all-reports-geo?window_days=${p.win}`),
    jget(`/api/outbreaks?eps_km=${p.eps}&min_samples=${p.min}&window_days=${p.win}&lang=${lng}`),
    jget("/api/farms"),
  ]);
  clearLayers();

  geo.points.forEach((pt) => {
    L.circleMarker([pt.lat, pt.lon], {
      radius: 5, color: pt.color, weight: 1, fillColor: pt.color, fillOpacity: .8,
    }).bindPopup(`<b>${pt.label}</b><br>conf ${(pt.confidence*100).toFixed(0)}% · ${pt.instances} inst`)
      .addTo(layers.reports);
  });

  const atRiskFarms = new Set(data.alerts.map((a) => a.farm));
  data.clusters.forEach((c) => {
    L.circle([c.centroid.lat, c.centroid.lon], {
      radius: Math.max(c.cluster_radius_km, 0.4) * 1000,
      color: "#e63946", weight: 2, fillColor: "#e63946", fillOpacity: .12,
    }).bindPopup(`<div class="cluster-pop"><b>${c.label} OUTBREAK</b><br>
      ${c.report_count} reports · ${c.total_instances} pests<br>
      severity: <b>${c.severity}</b> · newest ${c.newest_age_days}d ago<br>
      risk radius ${c.risk_radius_km} km</div>`).addTo(layers.clusters);
    L.circle([c.centroid.lat, c.centroid.lon], {
      radius: c.risk_radius_km * 1000,
      color: "#f59e0b", weight: 2, dashArray: "6 6", fill: false,
    }).addTo(layers.rings);
  });

  farmsData.farms.forEach((f) => {
    const risk = atRiskFarms.has(f.name);
    const mine = me.farm && f.id === me.farm.id;
    L.marker([f.lat, f.lon], { icon: farmIcon(risk, mine) })
      .bindPopup(`<b>${f.name}${mine ? " (you)" : ""}</b><br>${f.crop || ""} ${f.phone || ""}<br>` +
        (risk ? `<span style="color:#e63946">⚠ AT RISK</span>` : `no active threat`))
      .addTo(layers.farms);
  });

  // role-specific right panel
  if (me.role === "officer") {
    renderStats(data.stats);
    renderAlerts(data.alerts);
  } else {
    await renderFarmerPanel(p.win);
  }

  if (fit) {
    if (me.role === "farmer" && me.farm) {
      map.setView([me.farm.lat, me.farm.lon], 12);
    } else if (geo.points.length) {
      map.fitBounds(L.latLngBounds(geo.points.map((p) => [p.lat, p.lon])).pad(0.3));
    }
  }
}

function farmIcon(risk, mine) {
  const bg = risk ? "#e63946" : "#3a86ff";
  const ring = mine ? "box-shadow:0 0 0 3px rgba(34,197,94,.8),0 0 8px 2px rgba(0,0,0,.5);" : "";
  const glow = risk ? "box-shadow:0 0 8px 2px rgba(230,57,70,.7);" : "";
  return L.divIcon({
    className: "", iconSize: [16, 16], iconAnchor: [8, 8],
    html: `<div style="width:14px;height:14px;border-radius:3px;border:2px solid #fff;
      background:${bg};${mine ? ring : glow}"></div>`,
  });
}

function renderStats(s) {
  $("stats").innerHTML = `
    <div class="stat"><div class="n">${s.active_clusters}</div><div class="l">${t("stat_clusters")}</div></div>
    <div class="stat warn"><div class="n">${s.alerts_dispatched}</div><div class="l">${t("stat_alerts")}</div></div>
    <div class="stat crit"><div class="n">${s.farms_at_risk}</div><div class="l">${t("stat_atrisk")}</div></div>
    <div class="stat"><div class="n">${s.farms_total}</div><div class="l">${t("stat_farms")}</div></div>`;
}

async function renderFarmerPanel(win) {
  const lng = (typeof LANG !== "undefined" ? LANG : "en");
  const d = await jget(`/api/my-alerts?window_days=${win}&lang=${lng}`);
  const fs = $("farmer-status");
  fs.classList.remove("hidden");
  const farmName = d.farm ? d.farm.name : "";
  if (d.status === "at_risk") {
    fs.className = "farmer-status at_risk";
    fs.innerHTML = `<div class="fs-title">${t("farm_at_risk")}</div>
      <div class="fs-sub">${d.my_alerts.length} ${t("active_warnings")} ${farmName}. ${t("act_now")}</div>`;
  } else {
    fs.className = "farmer-status clear";
    fs.innerHTML = `<div class="fs-title">${t("farm_clear")}</div>
      <div class="fs-sub">${t("no_threats_near")} ${farmName} ${t("keep_monitoring")}</div>`;
  }
  renderAlerts(d.my_alerts, true);
}

function renderAlerts(alerts, farmer = false) {
  const el = $("alerts");
  if (!alerts.length) {
    el.innerHTML = farmer
      ? `<p class="muted">${t("no_warnings")}</p>`
      : `<p class="muted">${t("all_clear")}</p>`;
    return;
  }
  el.innerHTML = alerts.map((a) => `
    <div class="alert ${a.kind} ${a.severity}">
      <div class="a-head">
        <span class="a-farm">${farmer ? a.species_label : a.farm}</span>
        <span class="a-sev ${a.severity}">${a.severity}</span>
      </div>
      <div class="a-body">${a.headline}</div>
      <div class="a-body muted">📍 ${a.distance_km} km ${a.direction}` +
        (a.kind === "warning" ? ` · ${t("est_lead")}${a.lead_days_est} ${t("days")}` : "") + `</div>
      <div class="a-action">🔍 ${a.inspect}<br>✅ <b>${t("action")}:</b> ${a.action}</div>
    </div>`).join("");
}

/* -------------------------------------------------------------- controls */
function bindControls() {
  ["eps", "minpts", "window"].forEach((id) => {
    const inp = $(id), out = $(id + "-val");
    inp.addEventListener("input", () => { out.textContent = inp.value; });
    inp.addEventListener("change", () => refreshDashboard(false));
  });
}

async function resetDemo() {
  await authFetch("/api/reset?demo=true", { method: "POST" });
  toast("Demo scenario reloaded.");
  await refreshDashboard(true);
}

/* ----------------------------------------------------------------- init */
window.addEventListener("DOMContentLoaded", async () => {
  bindAuth();
  initPWA();
  if (token) { try { await enterApp(); } catch { doLogout(); } }
});

/* -------------------------------------------------- PWA install support */
let deferredPrompt = null;
function initPWA() {
  // register the service worker (enables offline + installability)
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }
  // capture the install prompt and show our own button
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    const b = $("btn-install");
    if (b) b.classList.remove("hidden");
  });
  const btn = $("btn-install");
  if (btn) {
    btn.addEventListener("click", async () => {
      if (!deferredPrompt) { toast("Use your browser menu → 'Add to Home screen'."); return; }
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      btn.classList.add("hidden");
    });
  }
  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    const b = $("btn-install"); if (b) b.classList.add("hidden");
    toast("PestWatch installed 📲");
  });
}
