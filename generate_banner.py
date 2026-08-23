"""Generate docs/banner.png (README hero) and labeled screenshot placeholders."""
import os
from PIL import Image, ImageDraw, ImageFont
from generate_icons import draw_icon

DOCS = os.path.join(os.path.dirname(__file__), "docs")
os.makedirs(DOCS, exist_ok=True)


def font(size, bold=False):
    for p in ([r"C:\Windows\Fonts\arialbd.ttf"] if bold else []) + [
            r"C:\Windows\Fonts\arial.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def grad(w, h, top, bot):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        f = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i]-top[i])*f) for i in range(3)))
    return img


# ---------------- hero banner ----------------
W, H = 1200, 380
img = grad(W, H, (14, 22, 40), (9, 14, 26))
d = ImageDraw.Draw(img)
# accent bar
d.rectangle([0, 0, W, 6], fill=(255, 90, 31))
# icon
icon = draw_icon(200).convert("RGBA")
img.paste(icon, (70, 90), icon)
# title + tagline
d.text((310, 96), "PestWatch", font=font(88, True), fill=(255, 255, 255))
d.text((314, 200), "Hyper-Local Crop Pest & Disease Early-Warning",
       font=font(30), fill=(180, 200, 230))
# chips
chips = ["YOLOv8 detection", "36-class disease", "DBSCAN outbreaks",
         "English + Telugu", "PWA + Android"]
x = 314
for c in chips:
    tw = d.textlength(c, font=font(22))
    d.rounded_rectangle([x, 258, x + tw + 30, 300], radius=20,
                        fill=(22, 34, 60), outline=(255, 90, 31))
    d.text((x + 15, 266), c, font=font(22), fill=(230, 237, 247))
    x += tw + 46
    if x > W - 200:
        break
img.save(os.path.join(DOCS, "banner.png"))
print("wrote docs/banner.png")

# ---------------- screenshot placeholders ----------------
shots = [
    ("01-login.png", "① Login screen", "officer / farmer roles"),
    ("02-dashboard.png", "② Officer dashboard", "outbreak map + clusters + alerts"),
    ("03-detection.png", "③ Detection result", "pest boxes + disease + treatment"),
    ("04-farmer.png", "④ Farmer view", "your-farm warnings (Telugu)"),
]
for fn, title, sub in shots:
    pw, ph = 900, 560
    p = grad(pw, ph, (17, 26, 46), (11, 17, 32))
    dd = ImageDraw.Draw(p)
    dd.rounded_rectangle([20, 20, pw-20, ph-20], radius=18, outline=(31, 43, 69), width=2)
    ic = draw_icon(96).convert("RGBA")
    p.paste(ic, ((pw-96)//2, 150), ic)
    for text, fsize, yy, col in [(title, 40, 280, (255, 255, 255)),
                                 (sub, 26, 340, (142, 160, 190)),
                                 (f"replace with a real screenshot -> docs/{fn}", 20, 470, (90, 105, 130))]:
        tw = dd.textlength(text, font=font(fsize, fsize == 40))
        dd.text(((pw-tw)//2, yy), text, font=font(fsize, fsize == 40), fill=col)
    p.save(os.path.join(DOCS, fn))
    print("wrote docs/" + fn)
