"""Generate assets/icon.png (1024) and assets/splash.png for @capacitor/assets."""
import os
from PIL import Image, ImageDraw
from generate_icons import draw_icon

OUT = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(OUT, exist_ok=True)

# 1024 launcher icon (full-bleed square, corners rounded by the generator)
icon = draw_icon(1024).convert("RGBA")
# fill fully so adaptive icon has no transparent corners
bg = Image.new("RGBA", (1024, 1024), (255, 90, 31, 255))
bg.paste(icon, (0, 0), icon)
bg.save(os.path.join(OUT, "icon.png"))
print("wrote assets/icon.png")

# splash: dark background with the bug centered
S = 2732
sp = Image.new("RGBA", (S, S), (11, 17, 32, 255))
badge = draw_icon(760).convert("RGBA")
sp.paste(badge, ((S - 760) // 2, (S - 760) // 2 - 120), badge)
d = ImageDraw.Draw(sp)
# simple wordmark
try:
    from PIL import ImageFont
    font = ImageFont.truetype("arial.ttf", 150)
except Exception:
    font = None
txt = "PestWatch"
if font:
    w = d.textlength(txt, font=font)
    d.text(((S - w) / 2, S // 2 + 360), txt, fill=(255, 255, 255, 255), font=font)
sp.save(os.path.join(OUT, "splash.png"))
sp.save(os.path.join(OUT, "splash-dark.png"))
print("wrote assets/splash.png")
