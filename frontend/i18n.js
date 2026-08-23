/* PestWatch bilingual dictionary — English + Telugu (తెలుగు). */
const I18N = {
  en: {
    tagline_short: "Crop Pest Outbreak Early-Warning",
    login: "Log in", farmer_signup: "Farmer sign-up",
    username: "Username", password: "Password",
    demo_accounts: "Demo accounts",
    demo_officer: "👨‍💼 Officer (dashboard)", demo_farmer: "🧑‍🌾 Farmer (reporter)",
    your_name: "Your name", farm_name: "Farm name", crop: "Crop",
    latitude: "Latitude", longitude: "Longitude", phone: "Phone",
    create_account: "Create farmer account",
    manage: "⚙ Manage", reset_demo: "Reset demo", logout: "Log out",
    step1: "1 · Capture & Detect",
    capture_hint: "Upload a field photo or video. The vision layer (YOLO) finds pests and a second model checks for leaf disease.",
    drop_label: "Click or drop a field photo or video",
    farm_reporter: "Farm / reporter", species_hint: "Species hint", auto_detect: "auto-detect",
    detect_report: "Detect & Report", random_spot: "🎲 Random spot",
    step2: "2 · Outbreak Map",
    lg_report: "report", lg_cluster: "cluster", lg_risk: "risk zone",
    lg_farm: "farm", lg_atrisk: "at-risk farm",
    ctrl_eps: "DBSCAN eps (km)", ctrl_min: "min reports", ctrl_win: "window (days)",
    step3: "3 · Early Warnings", step3_farm: "3 · Your Farm",
    alerts_dispatched: "Alerts dispatched", alerts_all: "Alerts dispatched (all farms)",
    warnings_for_you: "Warnings for you",
    manage_title: "⚙ Manage — Farms & Users", register_farm: "Register a new farm",
    add_farm: "➕ Add farm", registered_farms: "Registered farms",
    registered_users: "Registered users",
    users_hint: "Farmers self-register from the login screen. Officers maintain the platform.",
    tagline_officer: "District dashboard · Agriculture Department",
    tagline_farmer: "Report pests · get warnings for your farm",
    // dynamic
    stat_clusters: "Active clusters", stat_alerts: "Alerts sent",
    stat_atrisk: "Farms at risk", stat_farms: "Farms registered",
    pest_check: "🐛 Pest check", disease_check: "🦠 Disease check",
    confidence: "confidence", instances: "instance(s)", frames: "frames analysed",
    mode: "mode", action: "Action", inspect_icon: "🔍",
    farm_at_risk: "⚠ Your farm is at risk", farm_clear: "✅ No active threats",
    active_warnings: "active warning(s) near", act_now: "Act now.",
    no_threats_near: "No outbreaks near", keep_monitoring: "right now. Keep monitoring.",
    no_warnings: "No warnings for your farm. ✅",
    all_clear: "No outbreaks detected in this window. All clear ✅",
    disease_not_installed: "Disease model not installed.",
    est_lead: "est. lead time ~", days: "days",
    no_pest: "no pest", at_risk_lbl: "⚠ AT RISK", no_threat_lbl: "no active threat",
    you: "you", install_app: "📲 Install app",
  },
  te: {
    tagline_short: "పంట పురుగుల వ్యాప్తి ముందస్తు హెచ్చరిక",
    login: "లాగిన్", farmer_signup: "రైతు నమోదు",
    username: "వినియోగదారు పేరు", password: "పాస్‌వర్డ్",
    demo_accounts: "డెమో ఖాతాలు",
    demo_officer: "👨‍💼 అధికారి (డాష్‌బోర్డ్)", demo_farmer: "🧑‍🌾 రైతు (నివేదకుడు)",
    your_name: "మీ పేరు", farm_name: "పొలం పేరు", crop: "పంట",
    latitude: "అక్షాంశం", longitude: "రేఖాంశం", phone: "ఫోన్",
    create_account: "రైతు ఖాతా సృష్టించు",
    manage: "⚙ నిర్వహణ", reset_demo: "డెమో రీసెట్", logout: "లాగ్ అవుట్",
    step1: "1 · ఫోటో & గుర్తింపు",
    capture_hint: "పొలం ఫోటో లేదా వీడియో అప్‌లోడ్ చేయండి. YOLO నమూనా పురుగులను గుర్తిస్తుంది, రెండవ నమూనా ఆకు వ్యాధిని తనిఖీ చేస్తుంది.",
    drop_label: "ఫోటో లేదా వీడియో ఇక్కడ ఎంచుకోండి",
    farm_reporter: "పొలం / నివేదకుడు", species_hint: "జాతి సూచన", auto_detect: "స్వయంచాలకం",
    detect_report: "గుర్తించి నివేదించు", random_spot: "🎲 యాదృచ్ఛిక ప్రదేశం",
    step2: "2 · వ్యాప్తి పటం",
    lg_report: "నివేదిక", lg_cluster: "సమూహం", lg_risk: "ప్రమాద ప్రాంతం",
    lg_farm: "పొలం", lg_atrisk: "ప్రమాదంలో పొలం",
    ctrl_eps: "పరిధి (కి.మీ)", ctrl_min: "కనీస నివేదికలు", ctrl_win: "కాలం (రోజులు)",
    step3: "3 · ముందస్తు హెచ్చరికలు", step3_farm: "3 · మీ పొలం",
    alerts_dispatched: "పంపిన హెచ్చరికలు", alerts_all: "హెచ్చరికలు (అన్ని పొలాలు)",
    warnings_for_you: "మీ కోసం హెచ్చరికలు",
    manage_title: "⚙ నిర్వహణ — పొలాలు & వినియోగదారులు", register_farm: "కొత్త పొలం నమోదు",
    add_farm: "➕ పొలం చేర్చు", registered_farms: "నమోదైన పొలాలు",
    registered_users: "నమోదైన వినియోగదారులు",
    users_hint: "రైతులు లాగిన్ స్క్రీన్ నుండి స్వయంగా నమోదు అవుతారు. అధికారులు వేదికను నిర్వహిస్తారు.",
    tagline_officer: "జిల్లా డాష్‌బోర్డ్ · వ్యవసాయ శాఖ",
    tagline_farmer: "పురుగులను నివేదించండి · మీ పొలానికి హెచ్చరికలు పొందండి",
    stat_clusters: "క్రియాశీల సమూహాలు", stat_alerts: "పంపిన హెచ్చరికలు",
    stat_atrisk: "ప్రమాదంలో పొలాలు", stat_farms: "నమోదైన పొలాలు",
    pest_check: "🐛 పురుగు తనిఖీ", disease_check: "🦠 వ్యాధి తనిఖీ",
    confidence: "నమ్మకం", instances: "సందర్భాలు", frames: "ఫ్రేమ్‌లు విశ్లేషించబడ్డాయి",
    mode: "మోడ్", action: "చర్య", inspect_icon: "🔍",
    farm_at_risk: "⚠ మీ పొలం ప్రమాదంలో ఉంది", farm_clear: "✅ ప్రస్తుతం ప్రమాదం లేదు",
    active_warnings: "క్రియాశీల హెచ్చరిక(లు) దగ్గర", act_now: "వెంటనే చర్య తీసుకోండి.",
    no_threats_near: "సమీపంలో వ్యాప్తి లేదు", keep_monitoring: "ప్రస్తుతం. పర్యవేక్షిస్తూ ఉండండి.",
    no_warnings: "మీ పొలానికి హెచ్చరికలు లేవు. ✅",
    all_clear: "ఈ కాలంలో వ్యాప్తి కనుగొనబడలేదు. అంతా సురక్షితం ✅",
    disease_not_installed: "వ్యాధి నమూనా ఇన్‌స్టాల్ కాలేదు.",
    est_lead: "అంచనా సమయం ~", days: "రోజులు",
    no_pest: "పురుగు లేదు", at_risk_lbl: "⚠ ప్రమాదంలో", no_threat_lbl: "ప్రమాదం లేదు",
    you: "మీరు", install_app: "📲 యాప్ ఇన్‌స్టాల్ చేయి",
  },
};

let LANG = localStorage.getItem("pw_lang") || "en";

function t(key) {
  return (I18N[LANG] && I18N[LANG][key]) || (I18N.en[key] || key);
}

function applyStaticTranslations() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const k = el.getAttribute("data-i18n");
    if (I18N[LANG][k] !== undefined) el.textContent = I18N[LANG][k];
  });
  // reflect active button state on both toggles
  document.querySelectorAll(".lang-btn").forEach((b) =>
    b.classList.toggle("active", b.dataset.lang === LANG));
}

function setLang(lang) {
  LANG = lang;
  localStorage.setItem("pw_lang", lang);
  applyStaticTranslations();
  // let app.js refresh dynamic content if it's ready
  if (typeof onLangChange === "function") onLangChange();
}

function bindLangToggles() {
  document.querySelectorAll(".lang-btn").forEach((b) =>
    b.addEventListener("click", () => setLang(b.dataset.lang)));
  applyStaticTranslations();
}

document.addEventListener("DOMContentLoaded", bindLangToggles);
