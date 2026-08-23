"""Download real HEALTHY and DISEASED crop-leaf photos from the public
GVJahnavi/PlantVillage_dataset (38 named classes) for hands-on testing."""
import os, time, requests

DS = "GVJahnavi/PlantVillage_dataset"
BASE = os.path.join(os.path.dirname(__file__), "samples_test")
API = "https://datasets-server.huggingface.co/rows"
sess = requests.Session(); sess.headers["User-Agent"] = "PestWatch/1.0"

# class names in order
info = sess.get("https://datasets-server.huggingface.co/info", params={"dataset": DS}, timeout=60).json()
names = info["dataset_info"]["default"]["features"]["label"]["names"]
healthy_idx = {i for i, n in enumerate(names) if n.lower().endswith("healthy")}
print(f"{len(names)} classes, {len(healthy_idx)} healthy classes")

want = {"healthy": 6, "diseased": 6}
got = {"healthy": 0, "diseased": 0}
seen_h, seen_d = set(), set()   # spread across different crops
offset = 0

os.makedirs(os.path.join(BASE, "healthy_leaf"), exist_ok=True)
os.makedirs(os.path.join(BASE, "diseased_leaf"), exist_ok=True)

while (got["healthy"] < want["healthy"] or got["diseased"] < want["diseased"]) and offset < 60000:
    r = sess.get(API, params={"dataset": DS, "config": "default", "split": "train",
                              "offset": offset, "length": 100}, timeout=120)
    if r.status_code != 200:
        offset += 100; continue
    for item in r.json().get("rows", []):
        row = item["row"]; lab = row["label"]; nm = names[lab]
        if lab in healthy_idx:
            kind, folder, seen = "healthy", "healthy_leaf", seen_h
        else:
            kind, folder, seen = "diseased", "diseased_leaf", seen_d
        if got[kind] >= want[kind] or lab in seen:
            continue  # one per class for variety
        try:
            img = sess.get(row["image"]["src"], timeout=120)
            if img.status_code == 200 and len(img.content) > 2000:
                fn = f"{nm}.jpg".replace("/", "_")
                open(os.path.join(BASE, folder, fn), "wb").write(img.content)
                got[kind] += 1; seen.add(lab); print(f"  {kind:9s} {nm}")
        except Exception as e:
            print("  skip", e)
        time.sleep(0.1)
    offset += 100

print("done:", got)
