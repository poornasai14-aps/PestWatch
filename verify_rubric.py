"""Automated check that every Track-3 (Computer Vision) rubric item works."""
import io, json, sys, time, requests
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image

B = "http://127.0.0.1:8000"
results = []


def ok(n, name, cond, detail=""):
    results.append((n, name, cond, detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] #{n} {name}: {detail}")


# wait for server
for _ in range(30):
    try:
        if requests.get(B + "/api/health", timeout=3).ok:
            break
    except Exception:
        time.sleep(1)

h = requests.get(B + "/api/health").json()
ft = requests.post(B + "/api/auth/login", data={"username": "farmer", "password": "farmer123"}).json()["token"]
ot = requests.post(B + "/api/auth/login", data={"username": "officer", "password": "officer123"}).json()["token"]
HF = {"Authorization": "Bearer " + ft}
HO = {"Authorization": "Bearer " + ot}


def img_bytes():
    return open("samples_real/pest_00.jpg", "rb").read()


# ---- #2 Vision pipeline
ok(2, "Vision pipeline (YOLO detector + classifier loaded)",
   h["detector_mode"].startswith("yolo") and h["disease_model"],
   f"detector={h['detector_mode']}, disease_model={h['disease_model']}")

# ---- #1 Input stream: IMAGE
r = requests.post(B + "/api/detect", headers=HF,
                  files={"file": ("p.jpg", img_bytes(), "image/jpeg")},
                  data={"lat": 16.37, "lon": 80.49, "save": "false"}).json()
ok(1, "Input stream — IMAGE accepted",
   r.get("input_type") == "image" and "image_size" in r, str(r.get("image_size")))

# ---- #1 Input stream: VIDEO
try:
    vid = open("samples_test/pest_demo.mp4", "rb").read()
    rv = requests.post(B + "/api/detect", headers=HF,
                       files={"file": ("v.mp4", vid, "video/mp4")},
                       data={"lat": 16.37, "lon": 80.49, "save": "false"}).json()
    ok(1, "Input stream — VIDEO accepted",
       rv.get("input_type") == "video" and rv.get("frames_processed", 0) > 0,
       f"{rv.get('frames_processed')} frames, {rv.get('instance_count')} instances")
except Exception as e:
    ok(1, "Input stream — VIDEO accepted", False, str(e))

# ---- #3 Automated understanding: detection + classification
det_ok = "detections" in r and r["top_species"] is not None
cls_ok = r.get("disease") is not None and r["disease"].get("top_label")
ok(3, "Automated understanding — DETECTION", det_ok,
   f"species={r['top_label']}, instances={r['instance_count']}")
ok(3, "Automated understanding — CLASSIFICATION (disease)", bool(cls_ok),
   f"disease={r['disease']['top_label'] if cls_ok else None}")

# ---- #4 Measurable output: boxes, labels, confidence, counts
boxes = r.get("detections", [])
has_box = boxes and all(len(b["bbox"]) == 4 for b in boxes)
has_lab = boxes and all("label" in b and "confidence" in b for b in boxes)
ok(4, "Measurable output — bounding boxes", bool(has_box),
   f"{len(boxes)} boxes, e.g. {boxes[0]['bbox'] if boxes else None}")
ok(4, "Measurable output — labels+confidence+count", bool(has_lab and "instance_count" in r),
   f"count={r['instance_count']}, top_conf={r['top_confidence']}")

# ---- #6 Reliability: bad input handled, auth enforced, clustering stable
c_bad = requests.post(B + "/api/detect", headers=HF,
                      files={"file": ("x.txt", b"not an image", "text/plain")},
                      data={"lat": 16.3, "lon": 80.4, "save": "false"})
ok(6, "Robustness — bad file rejected (400)", c_bad.status_code == 400, f"HTTP {c_bad.status_code}")

c_noauth = requests.post(B + "/api/detect",
                         files={"file": ("p.jpg", img_bytes(), "image/jpeg")},
                         data={"lat": 16.3, "lon": 80.4})
ok(6, "Robustness — auth enforced (401)", c_noauth.status_code == 401, f"HTTP {c_noauth.status_code}")

c_403 = requests.post(B + "/api/reset?demo=true", headers=HF)
ok(6, "Robustness — role gating (farmer reset blocked 403)", c_403.status_code == 403, f"HTTP {c_403.status_code}")

ob = requests.get(B + "/api/outbreaks", headers=HO).json()
ok(6, "Robustness — clustering+alerting stable", "stats" in ob,
   f"clusters={ob['stats']['active_clusters']}, alerts={ob['stats']['alerts_dispatched']}")

# ---- Manage (officer maintenance)
fa = requests.post(B + "/api/farms", headers=HO,
                   data={"name": "Rubric Test Farm", "lat": 16.31, "lon": 80.44, "crop": "Maize"})
us = requests.get(B + "/api/users", headers=HO).json()
ok(6, "Officer Manage — add farm + list users",
   fa.json().get("ok") and len(us["users"]) >= 2, f"users={len(us['users'])}")

print("\n" + "=" * 60)
passed = sum(1 for _, _, c, _ in results if c)
print(f"RESULT: {passed}/{len(results)} checks passed")
print("=" * 60)
