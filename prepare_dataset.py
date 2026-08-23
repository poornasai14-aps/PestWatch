"""
Download a training-sized sample of `Francesco/pests-2xlvx` and convert it to
YOLO detection format (images/ + labels/ + data.yaml), ready for train.py.

COCO bbox [x,y,w,h] (absolute) -> YOLO [cls cx cy w h] (normalised).
"""
import json
import os
import time
import requests

DATASET = "Francesco/pests-2xlvx"
ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, "datasets", "pests")
N_TRAIN = int(os.environ.get("N_TRAIN", 500))
N_VAL = int(os.environ.get("N_VAL", 120))
ROWS_API = "https://datasets-server.huggingface.co/rows"

sess = requests.Session()
sess.headers["User-Agent"] = "PestWatch-demo/1.0"


def get_categories():
    info = sess.get("https://datasets-server.huggingface.co/info",
                    params={"dataset": DATASET}, timeout=60).json()
    feat = info["dataset_info"]["default"]["features"]
    return feat["objects"]["feature"]["category"]["names"]


def fetch_split(split, target, img_dir, lbl_dir):
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    saved, offset = 0, 0
    while saved < target:
        r = sess.get(ROWS_API, params={
            "dataset": DATASET, "config": "default", "split": split,
            "offset": offset, "length": 100}, timeout=120)
        if r.status_code != 200:
            print("  rows error", r.status_code); break
        rows = r.json().get("rows", [])
        if not rows:
            break
        for item in rows:
            if saved >= target:
                break
            row = item["row"]
            objs = row.get("objects", {})
            bboxes = objs.get("bbox", [])
            cats = objs.get("category", [])
            if not bboxes:
                continue  # skip background-only images
            W = row.get("width") or 640
            H = row.get("height") or 640
            try:
                img = sess.get(row["image"]["src"], timeout=120)
                if img.status_code != 200 or len(img.content) < 2000:
                    continue
                stem = f"{split}_{saved:04d}"
                with open(os.path.join(img_dir, stem + ".jpg"), "wb") as f:
                    f.write(img.content)
                lines = []
                for (x, y, bw, bh), c in zip(bboxes, cats):
                    cx = (x + bw / 2) / W
                    cy = (y + bh / 2) / H
                    nw, nh = bw / W, bh / H
                    if nw <= 0 or nh <= 0:
                        continue
                    lines.append(f"{int(c)} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
                with open(os.path.join(lbl_dir, stem + ".txt"), "w") as f:
                    f.write("\n".join(lines))
                saved += 1
                if saved % 25 == 0:
                    print(f"  {split}: {saved}/{target}")
            except Exception as e:
                print("  skip:", e)
            time.sleep(0.1)
        offset += 100
    return saved


def main():
    cats = get_categories()
    print(f"{len(cats)} classes")
    n1 = fetch_split("train", N_TRAIN,
                     os.path.join(OUT, "images", "train"),
                     os.path.join(OUT, "labels", "train"))
    n2 = fetch_split("validation", N_VAL,
                     os.path.join(OUT, "images", "val"),
                     os.path.join(OUT, "labels", "val"))
    data_yaml = os.path.join(OUT, "data.yaml")
    with open(data_yaml, "w") as f:
        f.write(f"path: {OUT.replace(os.sep, '/')}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write(f"nc: {len(cats)}\n")
        f.write("names:\n")
        for c in cats:
            f.write(f"  - {c}\n")
    json.dump({"categories": cats}, open(os.path.join(OUT, "categories.json"), "w"), indent=2)
    print(f"\nTrain={n1} Val={n2}\ndata.yaml -> {data_yaml}")


if __name__ == "__main__":
    main()
