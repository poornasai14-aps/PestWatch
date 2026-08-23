"""
Fine-tune YOLOv8 on the pest dataset with the field-condition augmentation
pipeline (answers the "poor lighting / complex backgrounds" challenge).

Defaults are CPU-friendly for a hackathon checkpoint. On a GPU box, raise
--epochs / --imgsz and download more images (N_TRAIN in prepare_dataset.py).

    python prepare_dataset.py          # build datasets/pests
    python train.py                    # trains, then installs models/best.pt

The trained best.pt is copied to models/best.pt, which detector.py auto-loads
on next server start (mode -> 'yolo-custom', real pest species).
"""
import argparse
import os
import shutil

from backend.augment import build_pipeline

ROOT = os.path.dirname(__file__)
DEFAULT_DATA = os.path.join(ROOT, "datasets", "pests", "data.yaml")
MODELS_DIR = os.path.join(ROOT, "models")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA, help="YOLO data.yaml")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--imgsz", type=int, default=416)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=0)  # 0 = Windows-safe
    args = ap.parse_args()

    if not os.path.exists(args.data):
        raise SystemExit(f"data.yaml not found: {args.data}\nRun: python prepare_dataset.py")

    from ultralytics import YOLO
    aug = build_pipeline()
    model = YOLO(args.model)
    results = model.train(
        data=args.data, epochs=args.epochs, imgsz=args.imgsz,
        batch=args.batch, device=args.device, workers=args.workers,
        project=os.path.join(ROOT, "runs"), name="pest_yolo", exist_ok=True,
        # field-condition augmentation (see backend/augment.py):
        hsv_h=aug["hsv_h"], hsv_s=aug["hsv_s"], hsv_v=aug["hsv_v"],
        degrees=aug["degrees"], translate=aug["translate"], scale=aug["scale"],
        shear=aug["shear"], fliplr=aug["fliplr"], mosaic=aug["mosaic"], mixup=aug["mixup"],
    )

    best = os.path.join(results.save_dir, "weights", "best.pt")
    os.makedirs(MODELS_DIR, exist_ok=True)
    if os.path.exists(best):
        shutil.copy(best, os.path.join(MODELS_DIR, "best.pt"))
        print(f"\n✅ Installed -> {os.path.join(MODELS_DIR, 'best.pt')}")
        print("Restart the server; detector will load it (mode: yolo-custom).")
    else:
        print("Training finished but best.pt not found at", best)


if __name__ == "__main__":
    main()
