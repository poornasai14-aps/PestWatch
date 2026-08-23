"""
Training-time augmentation pipeline.

This is our direct answer to the challenge as written: field pest models
underperform their benchmark scores because real photos have poor lighting and
complex backgrounds. We deliberately simulate those conditions during training
so ugly images do not surprise the model at inference time.

Each transform below maps to a real failure mode described in the overview:
  - brightness/contrast jitter  -> harsh midday sun, blown highlights, shadows
  - gaussian + motion blur       -> one-handed phone over a wind-blown plant
  - synthetic shadow injection   -> hard shadow edges across a single leaf
  - hue/saturation shift         -> green-on-green camouflage
  - rotation / scale jitter      -> arbitrary phone angles and distances

The functions use numpy only, so they run even before OpenCV is installed. When
OpenCV is available the app uses it for faster, higher-quality ops. Feed the
`build_pipeline()` output to your YOLO `train()` call (or apply per-image).
"""
from __future__ import annotations

import numpy as np

try:
    import cv2
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False


def brightness_contrast(img, brightness=0.0, contrast=0.0):
    """brightness in [-1,1], contrast in [-1,1]."""
    out = img.astype(np.float32)
    out = out * (1.0 + contrast) + brightness * 255.0
    return np.clip(out, 0, 255).astype(np.uint8)


def gaussian_blur(img, ksize=5):
    if _HAS_CV2:
        return cv2.GaussianBlur(img, (ksize | 1, ksize | 1), 0)
    # simple box-blur fallback
    k = np.ones((ksize, ksize), np.float32) / (ksize * ksize)
    out = img.astype(np.float32)
    pad = ksize // 2
    p = np.pad(out, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    res = np.zeros_like(out)
    for c in range(img.shape[2]):
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                res[i, j, c] = np.sum(p[i:i+ksize, j:j+ksize, c] * k)
    return np.clip(res, 0, 255).astype(np.uint8)


def motion_blur(img, degree=9, angle=0):
    if not _HAS_CV2:
        return gaussian_blur(img, ksize=degree)
    M = cv2.getRotationMatrix2D((degree / 2, degree / 2), angle, 1)
    kernel = np.diag(np.ones(degree))
    kernel = cv2.warpAffine(kernel, M, (degree, degree))
    kernel /= degree
    return cv2.filter2D(img, -1, kernel)


def inject_shadow(img, strength=0.5):
    """Darken a random half-plane to mimic a hard shadow edge across the leaf."""
    h, w = img.shape[:2]
    mask = np.ones((h, w), np.float32)
    x1, x2 = np.random.randint(0, w), np.random.randint(0, w)
    for y in range(h):
        cut = int(x1 + (x2 - x1) * y / max(h - 1, 1))
        mask[y, :cut] = 1.0 - strength
    out = img.astype(np.float32) * mask[:, :, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def hue_saturation(img, hue_shift=0, sat_scale=1.0):
    if not _HAS_CV2:
        return img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
    hsv[..., 1] = np.clip(hsv[..., 1] * sat_scale, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def random_augment(img, rng: np.random.RandomState | None = None):
    """Apply a random field-condition augmentation stack to one image."""
    rng = rng or np.random.RandomState()
    out = img
    if rng.rand() < 0.8:
        out = brightness_contrast(out, brightness=rng.uniform(-0.35, 0.35),
                                  contrast=rng.uniform(-0.3, 0.3))
    if rng.rand() < 0.4:
        out = motion_blur(out, degree=int(rng.randint(5, 13)),
                          angle=float(rng.randint(0, 180)))
    elif rng.rand() < 0.4:
        out = gaussian_blur(out, ksize=int(rng.randint(3, 7)))
    if rng.rand() < 0.5:
        out = inject_shadow(out, strength=rng.uniform(0.3, 0.6))
    if rng.rand() < 0.5:
        out = hue_saturation(out, hue_shift=int(rng.randint(-10, 10)),
                             sat_scale=rng.uniform(0.7, 1.3))
    return out


def build_pipeline() -> dict:
    """
    Returns the augmentation hyper-parameters to pass to YOLOv8's train() call
    (ultralytics reads these directly), aligned with the transforms above.
    """
    return {
        "hsv_h": 0.015,     # hue jitter  -> camouflage robustness
        "hsv_s": 0.7,       # saturation  -> lighting robustness
        "hsv_v": 0.4,       # value/brightness -> harsh sun / shadow
        "degrees": 10.0,    # rotation    -> arbitrary phone angle
        "translate": 0.1,
        "scale": 0.5,       # scale jitter -> distance from plant
        "shear": 2.0,
        "fliplr": 0.5,
        "mosaic": 1.0,      # background randomisation -> complex backgrounds
        "mixup": 0.15,
        "blur": 0.1,        # motion/gaussian blur -> wind + one-handed capture
    }
