"""
Download a small sample of REAL pest images from the public HuggingFace
dataset `Francesco/pests-2xlvx` (object-detection, 29 pest species, with
bounding boxes) via the datasets-server API. No auth required.

Saves images to samples_real/ and a labels.json manifest (category names +
bboxes) that could seed a YOLO training set.
"""
import json
import os
import time
import requests

DATASET = "Francesco/pests-2xlvx"
OUT = os.path.join(os.path.dirname(__file__), "samples_real")
N = 36
ROWS_API = "https://datasets-server.huggingface.co/rows"

os.makedirs(OUT, exist_ok=True)
sess = requests.Session()
sess.headers["User-Agent"] = "PestWatch-demo/1.0"

# category names (index -> name) from the dataset info
info = sess.get("https://datasets-server.huggingface.co/info",
                params={"dataset": DATASET}, timeout=60).json()
feat = info["dataset_info"]["default"]["features"]
cats = feat["objects"]["feature"]["category"]["names"]
print(f"{len(cats)} categories, e.g. {cats[1:5]}")

manifest = []
saved = 0
offset = 0
while saved < N:
    r = sess.get(ROWS_API, params={
        "dataset": DATASET, "config": "default", "split": "train",
        "offset": offset, "length": 20}, timeout=90)
    r.raise_for_status()
    rows = r.json().get("rows", [])
    if not rows:
        break
    for item in rows:
        if saved >= N:
            break
        row = item["row"]
        src = row["image"]["src"]
        objs = row.get("objects", {})
        labels = [cats[c] for c in objs.get("category", [])]
        try:
            img = sess.get(src, timeout=90)
            if img.status_code != 200 or len(img.content) < 2000:
                continue
            fn = f"pest_{saved:02d}.jpg"
            with open(os.path.join(OUT, fn), "wb") as f:
                f.write(img.content)
            manifest.append({
                "file": fn,
                "labels": labels,
                "bboxes": objs.get("bbox", []),
                "size": {"w": row.get("width"), "h": row.get("height")},
            })
            saved += 1
            print(f"  [{saved:2d}/{N}] {fn}  <- {labels[:3]}")
        except Exception as e:
            print("  skip:", e)
        time.sleep(0.15)
    offset += 20

with open(os.path.join(OUT, "labels.json"), "w") as f:
    json.dump({"dataset": DATASET, "categories": cats, "items": manifest}, f, indent=2)

print(f"\nDone: {saved} real pest images -> {OUT}")
