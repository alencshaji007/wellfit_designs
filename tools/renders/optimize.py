"""Create responsive AVIF + WebP variants. Usage: optimize.py SRC_IMAGE OUT_DIR BASENAME [maxwidth]
Writes BASENAME-<w>.avif / .webp for a fixed width ladder (never upscales) and prints JSON metadata."""
import json, os, sys
from PIL import Image, ImageOps
src, outdir, base = sys.argv[1], sys.argv[2], sys.argv[3]
maxw = int(sys.argv[4]) if len(sys.argv) > 4 else 99999
LADDER = [480, 800, 1200, 1600, 1920]
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
W, H = im.size
top = min(W, maxw)
widths = sorted(set([w for w in LADDER if w <= top * 0.85] + [top]))
os.makedirs(outdir, exist_ok=True)
out = {'base': base, 'w': W, 'h': H, 'widths': []}
for w in widths:
    h = round(H * w / W)
    r = im.resize((w, h), Image.LANCZOS) if w != W else im
    r.save(os.path.join(outdir, f'{base}-{w}.webp'), 'WEBP', quality=84, method=6)
    r.save(os.path.join(outdir, f'{base}-{w}.avif'), 'AVIF', quality=64, speed=6)
    out['widths'].append(w)
print(json.dumps(out))
