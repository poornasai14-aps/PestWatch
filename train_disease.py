"""
Train a YOLOv8 classification model on the PlantVillage subset and install it as
models/disease_best.pt (loaded automatically by disease_classifier.py).

    python prepare_disease.py    # build datasets/disease
    python train_disease.py      # trains + installs the model
"""
import argparse, os, shutil

ROOT = os.path.dirname(__file__)
DATA = os.path.join(ROOT, "datasets", "disease")
MODELS = os.path.join(ROOT, "models")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--imgsz", type=int, default=160)
    ap.add_argument("--model", default="yolov8n-cls.pt")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=0)
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(DATA, "train")):
        raise SystemExit("datasets/disease not found. Run: python prepare_disease.py")

    from ultralytics import YOLO
    model = YOLO(args.model)
    results = model.train(
        data=DATA, epochs=args.epochs, imgsz=args.imgsz,
        device=args.device, workers=args.workers,
        project=os.path.join(ROOT, "runs"), name="disease_cls", exist_ok=True,
        # light color/geometry augmentation (leaf disease is colour/texture based)
        hsv_h=0.015, hsv_s=0.6, hsv_v=0.4, fliplr=0.5, degrees=15, erasing=0.2,
    )
    best = os.path.join(results.save_dir, "weights", "best.pt")
    os.makedirs(MODELS, exist_ok=True)
    if os.path.exists(best):
        shutil.copy(best, os.path.join(MODELS, "disease_best.pt"))
        print(f"\n✅ Installed -> {os.path.join(MODELS, 'disease_best.pt')}")
    else:
        print("best.pt not found at", best)


if __name__ == "__main__":
    main()
