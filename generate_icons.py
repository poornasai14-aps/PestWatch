"""Generate PestWatch PWA app icons (192 & 512) — a bug on an orange tile."""
import os, math
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "frontend")


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded orange gradient background
    r = int(size * 0.22)
    for y in range(size):
        f = y / size
        col = (int(255 - f * 20), int(90 + f * 90), int(31 + f * 10))
        d.line([(0, y), (size, y)], fill=col + (255,))
    # round the corners by masking
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=r, fill=255)
    img.putalpha(mask)

    d = ImageDraw.Draw(img)
    cx, cy = size / 2, size * 0.54
    bw, bh = size * 0.30, size * 0.42          # bug body
    white = (255, 255, 255, 255)
    dark = (30, 20, 15, 255)

    # legs (white)
    lw = max(2, int(size * 0.018))
    for i, ly in enumerate([-0.13, 0.0, 0.13]):
        yy = cy + bh * ly
        d.line([(cx - bw * 0.55, yy - bh*0.06), (cx - bw * 1.05, yy - bh*0.14)], fill=white, width=lw)
        d.line([(cx + bw * 0.55, yy - bh*0.06), (cx + bw * 1.05, yy - bh*0.14)], fill=white, width=lw)
    # antennae
    d.line([(cx - bw*0.18, cy - bh*0.52), (cx - bw*0.5, cy - bh*0.78)], fill=white, width=lw)
    d.line([(cx + bw*0.18, cy - bh*0.52), (cx + bw*0.5, cy - bh*0.78)], fill=white, width=lw)

    # body (white ellipse) + head
    d.ellipse([cx - bw/2, cy - bh/2, cx + bw/2, cy + bh/2], fill=white)
    hr = bw * 0.42
    d.ellipse([cx - hr, cy - bh/2 - hr*1.1, cx + hr, cy - bh/2 + hr*0.9], fill=white)
    # body segments (dark lines)
    for s in [-0.18, 0.06, 0.30]:
        yy = cy + bh * s
        d.line([(cx - bw*0.42, yy), (cx + bw*0.42, yy)], fill=dark, width=max(2, int(size*0.012)))
    # center line
    d.line([(cx, cy - bh*0.30), (cx, cy + bh*0.42)], fill=dark, width=max(2, int(size*0.012)))
    return img


for s in (192, 512):
    draw_icon(s).save(os.path.join(OUT, f"icon-{s}.png"))
    print("wrote", f"icon-{s}.png")
