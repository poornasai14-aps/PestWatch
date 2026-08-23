"""Grab real 'no pest' (background / no-annotation) images from the same
pests-2xlvx dataset, to test the 'healthy' path."""
import os, time, requests

DATASET = "Francesco/pests-2xlvx"
OUT = os.path.join(os.path.dirname(__file__), "samples_test", "healthy")
N = 6
os.makedirs(OUT, exist_ok=True)
sess = requests.Session(); sess.headers["User-Agent"] = "PestWatch/1.0"

saved, offset = 0, 0
while saved < N and offset < 3000:
    r = sess.get("https://datasets-server.huggingface.co/rows", params={
        "dataset": DATASET, "config": "default", "split": "train",
        "offset": offset, "length": 100}, timeout=120)
    for item in r.json().get("rows", []):
        if saved >= N:
            break
        row = item["row"]
        if row.get("objects", {}).get("bbox"):
            continue  # has a pest -> skip; we want empty ones
        try:
            img = sess.get(row["image"]["src"], timeout=120)
            if img.status_code == 200 and len(img.content) > 2000:
                with open(os.path.join(OUT, f"healthy_{saved:02d}.jpg"), "wb") as f:
                    f.write(img.content)
                saved += 1; print("healthy", saved)
        except Exception as e:
            print("skip", e)
        time.sleep(0.1)
    offset += 100
print("done", saved)
