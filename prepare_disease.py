"""
Download the FULL PlantVillage set (38 classes / 14 crops) as an ImageFolder
classification dataset (datasets/disease/{train,val}/<class>/*.jpg) for
YOLOv8-cls training. Scans /rows sequentially (dataset is ordered by class) and
buckets images into each target class, stopping once all are filled.
Folder names match the keys in backend/diseases.py.
"""
import os, time, requests

DS = "GVJahnavi/PlantVillage_dataset"
OUT = os.path.join(os.path.dirname(__file__), "datasets", "disease")
ROWS = "https://datasets-server.huggingface.co/rows"
PER_TRAIN = int(os.environ.get("PER_TRAIN", 50))
PER_VAL = int(os.environ.get("PER_VAL", 12))
NEED = PER_TRAIN + PER_VAL
MAXOFF = 60000

# label_index (PlantVillage order) -> short class name == diseases.py key
TARGETS = {
    0: "apple_scab", 1: "apple_black_rot", 2: "apple_cedar_rust", 3: "apple_healthy",
    4: "blueberry_healthy",
    5: "cherry_powdery_mildew", 6: "cherry_healthy",
    7: "corn_gray_leaf_spot", 8: "corn_common_rust", 9: "corn_northern_blight", 10: "corn_healthy",
    11: "grape_black_rot", 12: "grape_esca", 13: "grape_leaf_blight", 14: "grape_healthy",
    15: "orange_citrus_greening",
    16: "peach_bacterial_spot", 17: "peach_healthy",
    18: "pepper_bacterial_spot", 19: "pepper_healthy",
    20: "potato_early_blight", 21: "potato_late_blight", 22: "potato_healthy",
    23: "raspberry_healthy", 24: "soybean_healthy",
    25: "squash_powdery_mildew",
    26: "strawberry_leaf_scorch", 27: "strawberry_healthy",
    28: "tomato_bacterial_spot", 29: "tomato_early_blight", 30: "tomato_late_blight",
    31: "tomato_leaf_mold", 32: "tomato_septoria_spot", 33: "tomato_spider_mites",
    34: "tomato_target_spot", 35: "tomato_yellow_leaf_curl_virus", 36: "tomato_mosaic_virus",
    37: "tomato_healthy",
}

sess = requests.Session(); sess.headers["User-Agent"] = "PestWatch/1.0"
count = {k: 0 for k in TARGETS}
offset = 0

while any(count[k] < NEED for k in TARGETS) and offset < MAXOFF:
    try:
        r = sess.get(ROWS, params={"dataset": DS, "config": "default", "split": "train",
                                   "offset": offset, "length": 100}, timeout=120)
    except Exception:
        offset += 100; continue
    if r.status_code != 200:
        offset += 100; continue
    batch = r.json().get("rows", [])
    if not batch:
        break
    for item in batch:
        lab = item["row"]["label"]
        if lab not in TARGETS or count[lab] >= NEED:
            continue
        cls = TARGETS[lab]; i = count[lab]
        split = "train" if i < PER_TRAIN else "val"
        d = os.path.join(OUT, split, cls); os.makedirs(d, exist_ok=True)
        try:
            img = sess.get(item["row"]["image"]["src"], timeout=120)
            if img.status_code == 200 and len(img.content) > 1500:
                open(os.path.join(d, f"{cls}_{i:03d}.jpg"), "wb").write(img.content)
                count[lab] += 1
        except Exception as e:
            print("  skip", e)
        time.sleep(0.03)
    filled = sum(1 for k in TARGETS if count[k] >= NEED)
    print(f"  offset {offset}: {filled}/{len(TARGETS)} classes filled")
    offset += 100

print("\nPer-class counts:")
for k, v in TARGETS.items():
    print(f"  {v:30s} {count[k]}")
print("Total:", sum(count.values()), "| classes:", len(TARGETS))
