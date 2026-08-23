"""
PestWatch — Hyper-Local Crop Pest Outbreak Early-Warning System.
FastAPI backend wiring the full pipeline:

  capture -> detect (Layer 1) -> aggregate -> DBSCAN cluster -> risk radius ->
  farm alerting (Layer 2).

Auth: two roles — 'officer' (dashboard/admin) and 'farmer' (reporter). See auth.py.
"""
from __future__ import annotations

import base64
import io
import os
import tempfile
import time
import uuid

import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

from . import store, seed as seed_mod, species as species_kb, auth
from .detector import get_detector
from .disease_classifier import get_classifier
from .clustering import build_clusters, generate_alerts, DEFAULT_WINDOW_DAYS

ROOT = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
UPLOAD_DIR = os.environ.get("PESTWATCH_UPLOADS") or os.path.join(ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="PestWatch API", version="1.1")

# Allow the mobile app / PWA (any origin) to call the API when hosted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def _no_cache(request, call_next):
    """Serve fresh assets every load so UI/JS updates are never stale-cached.
    The service worker script is exempted — some browsers refuse to register a
    worker whose script is served with 'no-store'."""
    resp = await call_next(request)
    if request.url.path == "/sw.js":
        resp.headers["Cache-Control"] = "no-cache"
    else:
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.on_event("startup")
def _startup():
    store.init_db()
    auth.init_auth()
    if store.counts()["reports"] == 0:
        seed_mod.seed(reset=True)
    # seed demo accounts, linking the demo farmer to an existing farm
    _relink_farmer()
    auth.seed_users(farm_id_for_farmer=_ravi_id())


def _ravi_id():
    ravi = next((f for f in store.get_farms() if "Ravi" in f["name"]), None)
    return ravi["id"] if ravi else None


def _relink_farmer():
    """Keep the demo farmer pointed at the current Ravi farm (ids change on reseed)."""
    rid = _ravi_id()
    if rid:
        auth.set_farm("farmer", rid)


# --------------------------------------------------------- auth dependencies
def _token(authorization: str | None) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:]
    return ""


def current_user(authorization: str | None = Header(default=None)) -> dict | None:
    return auth.user_from_token(_token(authorization))


def require_user(user: dict | None = Depends(current_user)) -> dict:
    if not user:
        raise HTTPException(401, "login required")
    return user


def require_officer(user: dict = Depends(require_user)) -> dict:
    if user["role"] != "officer":
        raise HTTPException(403, "officer role required")
    return user


# --------------------------------------------------------------- utilities
def _to_bgr(data: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    arr = np.array(img)
    return arr[:, :, ::-1].copy()


VIDEO_EXT = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v")


def _is_video(filename: str) -> bool:
    return (filename or "").lower().endswith(VIDEO_EXT)


def _annotate_bgr(bgr: np.ndarray, detections: list, color=(70, 57, 230)) -> str:
    """Draw boxes+labels on a BGR frame and return a base64 data URI (JPEG)."""
    import cv2
    frame = bgr.copy()
    for d in detections:
        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        tag = f"{d['label']} {int(d['confidence']*100)}%"
        cv2.rectangle(frame, (x1, max(y1 - 20, 0)), (x1 + 9 * len(tag), y1), color, -1)
        cv2.putText(frame, tag, (x1 + 3, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


# ------------------------------------------------------------------ auth API
@app.post("/api/auth/login")
def api_login(username: str = Form(...), password: str = Form(...)):
    res = auth.login(username, password)
    if not res:
        raise HTTPException(401, "invalid username or password")
    return res


@app.post("/api/auth/logout")
def api_logout(authorization: str | None = Header(default=None)):
    auth.logout(_token(authorization))
    return {"ok": True}


@app.get("/api/auth/me")
def api_me(user: dict = Depends(require_user)):
    u = auth.public(user)
    if u.get("farm_id"):
        farm = next((f for f in store.get_farms() if f["id"] == u["farm_id"]), None)
        u["farm"] = farm
    return u


@app.post("/api/auth/register")
def api_register(username: str = Form(...), password: str = Form(...),
                 full_name: str = Form(""), phone: str = Form(""),
                 farm_name: str = Form(""), crop: str = Form(""),
                 lat: float = Form(None), lon: float = Form(None)):
    """Open sign-up for FARMERS only. Optionally registers their farm too."""
    farm_id = None
    if farm_name and lat is not None and lon is not None:
        farm_id = store.add_farm(farm_name, lat, lon, crop, phone)
    try:
        user = auth.create_user(username, password, "farmer",
                                full_name=full_name, farm_id=farm_id, phone=phone)
    except ValueError as e:
        raise HTTPException(400, str(e))
    res = auth.login(username, password)
    return res or {"user": user}


# ------------------------------------------------------------------ routes
@app.get("/api/health")
def health():
    det = get_detector()
    return {
        "status": "ok",
        "detector_mode": det.mode,
        "disease_model": get_classifier().available,
        "species_supported": len(species_kb.PEST_CLASSES),
        **store.counts(),
    }


@app.get("/api/species")
def list_species():
    return [species_kb.get(k) for k in species_kb.SPECIES if k != "healthy"]


@app.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
    farm_name: str = Form(""),
    hint_species: str = Form(""),
    save: bool = Form(True),
    lang: str = Form("en"),
    user: dict = Depends(require_user),
):
    """Stage 1-3: detect pests in an uploaded photo and (optionally) record it."""
    data = await file.read()
    hint = hint_species if hint_species in species_kb.SPECIES else None
    annotated = None
    is_video = _is_video(file.filename)

    if is_video:
        # ---- VIDEO input: sample frames, detect across them, aggregate -------
        tmp = tempfile.NamedTemporaryFile(delete=False,
                                          suffix=os.path.splitext(file.filename)[1] or ".mp4")
        try:
            tmp.write(data); tmp.close()
            result = get_detector().detect_video(tmp.name, hint_species=hint)
            frame = result.pop("best_frame", None)
            bgr = frame if frame is not None else np.zeros((10, 10, 3), np.uint8)
            if frame is not None:
                annotated = _annotate_bgr(frame, result["detections"])
        except Exception as e:
            raise HTTPException(400, f"Could not process video: {e}")
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
    else:
        # ---- IMAGE input ----------------------------------------------------
        try:
            bgr = _to_bgr(data)
        except Exception:
            raise HTTPException(400, "Could not read image")
        result = get_detector().detect(bgr, hint_species=hint)

    # Second model: leaf-disease classifier (answers "is this leaf diseased?").
    disease = get_classifier().classify(bgr, lang=lang)

    image_path = None
    report_id = None
    reporter = farm_name or user.get("full_name") or user.get("username")
    if save and result["top_species"] != "healthy":
        fname = f"{uuid.uuid4().hex}_{file.filename or 'img.jpg'}"
        image_path = os.path.join("uploads", fname)
        with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
            f.write(data)
        report_id = store.add_report(
            species=result["top_species"],
            lat=lat, lon=lon,
            confidence=result["top_confidence"],
            instance_count=result["instance_count"],
            detector_mode=result["mode"],
            farm_name=reporter,
            image_path=image_path,
        )

    return {
        "report_id": report_id,
        "input_type": "video" if is_video else "image",
        "annotated_image": annotated,   # server-drawn frame (video); None for images
        "location": {"lat": lat, "lon": lon},
        "saved": report_id is not None,
        "species_info": species_kb.get(result["top_species"], lang),
        "disease": disease,   # None if the disease model isn't installed
        **result,
    }


@app.get("/api/reports")
def reports(species: str = "", days: float = DEFAULT_WINDOW_DAYS,
            user: dict = Depends(require_user)):
    rs = store.get_reports(species=species or None, since_days=days)
    return {"count": len(rs), "reports": rs}


@app.get("/api/farms")
def farms(user: dict = Depends(require_user)):
    return {"farms": store.get_farms()}


@app.post("/api/farms")
def add_farm(name: str = Form(...), lat: float = Form(...), lon: float = Form(...),
             crop: str = Form(""), phone: str = Form(""),
             user: dict = Depends(require_officer)):
    fid = store.add_farm(name, lat, lon, crop, phone)
    return {"id": fid, "ok": True}


@app.get("/api/outbreaks")
def outbreaks(eps_km: float = 2.5, min_samples: int = 3,
              window_days: float = DEFAULT_WINDOW_DAYS, lang: str = "en",
              user: dict = Depends(require_user)):
    """Stage 4-5: cluster + risk projection + alerts (the officer dashboard feed)."""
    reports_all = store.get_reports(since_days=window_days)
    farms_all = store.get_farms()
    clusters = build_clusters(reports_all, eps_km=eps_km,
                              min_samples=min_samples, window_days=window_days)
    alerts = generate_alerts(clusters, farms_all, lang=lang)

    slim_clusters = []
    for c in clusters:
        c2 = {k: v for k, v in c.items() if k != "members"}
        c2["label"] = species_kb.get(c["species"], lang)["label"]
        c2["points"] = [{"lat": m["lat"], "lon": m["lon"],
                         "ts": m["ts"], "confidence": m["confidence"]}
                        for m in c["members"]]
        slim_clusters.append(c2)

    at_risk_farms = sorted({a["farm"] for a in alerts})
    return {
        "generated_at": time.time(),
        "window_days": window_days,
        "reports_in_window": len(reports_all),
        "clusters": slim_clusters,
        "alerts": alerts,
        "stats": {
            "active_clusters": len(clusters),
            "alerts_dispatched": len(alerts),
            "farms_at_risk": len(at_risk_farms),
            "farms_total": len(farms_all),
        },
    }


@app.get("/api/my-alerts")
def my_alerts(window_days: float = DEFAULT_WINDOW_DAYS, lang: str = "en",
              user: dict = Depends(require_user)):
    """Farmer view: only the warnings that concern this farmer's own farm."""
    farms_all = store.get_farms()
    my_farm = next((f for f in farms_all if f["id"] == user.get("farm_id")), None)
    reports_all = store.get_reports(since_days=window_days)
    clusters = build_clusters(reports_all, window_days=window_days)

    my_alerts_list = []
    if my_farm:
        my_alerts_list = generate_alerts(clusters, [my_farm], lang=lang)

    slim = [{k: v for k, v in c.items() if k != "members"} | {
        "points": [{"lat": m["lat"], "lon": m["lon"]} for m in c["members"]]
    } for c in clusters]
    return {
        "farm": my_farm,
        "my_alerts": my_alerts_list,
        "nearby_clusters": slim,
        "status": ("at_risk" if my_alerts_list else "clear"),
    }


@app.get("/api/all-reports-geo")
def all_reports_geo(window_days: float = DEFAULT_WINDOW_DAYS,
                    user: dict = Depends(require_user)):
    rs = store.get_reports(since_days=window_days)
    return {"points": [{
        "id": r["id"], "species": r["species"],
        "label": species_kb.get(r["species"])["label"],
        "color": species_kb.get(r["species"])["color"],
        "lat": r["lat"], "lon": r["lon"], "ts": r["ts"],
        "confidence": r["confidence"], "instances": r["instance_count"],
    } for r in rs]}


@app.get("/api/users")
def list_users(user: dict = Depends(require_officer)):
    from .store import _conn
    with _conn() as c:
        rows = c.execute(
            "SELECT id,username,full_name,role,phone,farm_id FROM users").fetchall()
    return {"users": [dict(r) for r in rows]}


@app.post("/api/reset")
def reset(demo: bool = True, user: dict = Depends(require_officer)):
    if demo:
        seed_mod.seed(reset=True)
        _relink_farmer()   # re-point farmer at the freshly seeded farm
    else:
        store.reset()
        store.init_db()
    return {"ok": True, **store.counts()}


# --------------------------------------------------------------- static UI
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
