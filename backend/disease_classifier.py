"""
Leaf-disease classifier (second vision model, complements the pest detector).

Runs a YOLOv8 classification model (models/disease_best.pt) on the whole leaf
image and returns the most likely disease class + confidence. Answers a
different question from the pest detector: "is this leaf diseased?" rather than
"is there an insect?".

Gracefully disabled if the model file or ultralytics isn't available.
"""
from __future__ import annotations

import os
from typing import Dict, Optional

import numpy as np

from . import diseases as disease_kb

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "disease_best.pt")


class DiseaseClassifier:
    def __init__(self):
        self.available = False
        self.model = None
        self._load()

    def _load(self):
        if not os.path.exists(MODEL_PATH):
            return
        try:
            from ultralytics import YOLO
            self.model = YOLO(MODEL_PATH)
            self.available = True
        except Exception:
            self.model = None
            self.available = False

    def classify(self, image_bgr: np.ndarray, topk: int = 3, lang: str = "en") -> Optional[Dict]:
        if not self.available:
            return None
        try:
            res = self.model.predict(image_bgr, verbose=False)[0]
            probs = res.probs
            names = self.model.names
            top1 = int(probs.top1)
            key = names[top1]
            conf = float(probs.top1conf)
            info = disease_kb.get(key, lang)
            toplist = []
            for idx in list(probs.top5)[:topk]:
                nm = names[int(idx)]
                toplist.append({"key": nm, "label": disease_kb.get(nm, lang)["label"],
                                "confidence": round(float(probs.data[int(idx)]), 3)})
            return {
                "available": True,
                "top_key": key,
                "top_label": info["label"],
                "confidence": round(conf, 3),
                "healthy": info["healthy"],
                "crop": info["crop"],
                "note": info["note"],
                "action": info["action"],
                "color": info["color"],
                "topk": toplist,
            }
        except Exception:
            return None


_clf: Optional[DiseaseClassifier] = None


def get_classifier() -> DiseaseClassifier:
    global _clf
    if _clf is None:
        _clf = DiseaseClassifier()
    return _clf
