"""Draw an original, text-free architectural floor-plan sheet used as a texture in the design-desk render."""
import math, sys
from PIL import Image, ImageDraw
W, H = 2400, 1700
im = Image.new('RGB', (W, H), (244, 241, 234))
d = ImageDraw.Draw(im)
ink = (58, 56, 54); soft = (150, 146, 140); faint = (205, 200, 192)
# sheet border + title block lines (no text)
d.rectangle([60, 60, W - 60, H - 60], outline=ink, width=4)
d.rectangle([W - 520, H - 260, W - 60, H - 60], outline=ink, width=3)
for y in (H - 210, H - 160, H - 110):
    d.line([W - 520, y, W - 60, y], fill=soft, width=2)
# grid dots
for x in range(140, W - 560, 60):
    for y in range(140, H - 120, 60):
        d.point((x, y), fill=faint)
ox, oy, s = 220, 200, 95  # origin and scale (px per metre)
def P(x, y): return (ox + x * s, oy + y * s)
def wall(x0, y0, x1, y1, t=0.25):
    a, b = P(min(x0, x1), min(y0, y1)), P(max(x0, x1), max(y0, y1))
    if x0 == x1: d.rectangle([a[0] - t * s / 2, a[1], a[0] + t * s / 2, b[1]], fill=ink)
    else: d.rectangle([a[0], a[1] - t * s / 2, b[0], a[1] + t * s / 2], fill=ink)
# outer walls (17 x 12 m)
for seg in [(0, 0, 17, 0), (0, 12, 17, 12), (0, 0, 0, 12), (17, 0, 17, 12)]:
    wall(*seg, t=0.3)
# interior walls
for seg in [(6, 0, 6, 5), (6, 7, 6, 12), (11, 0, 11, 4.2), (11, 5.8, 11, 12), (0, 5, 4.5, 5), (11, 7, 17, 7), (13.5, 7, 13.5, 12)]:
    wall(*seg, t=0.15)
# openings (white gaps) with door swings
def door(x, y, r, start, sweep):
    cx, cy = P(x, y)
    d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=ink)
    d.arc([cx - r * s, cy - r * s, cx + r * s, cy + r * s], start, start + sweep, fill=soft, width=2)
    a = math.radians(start + sweep)
    d.line([cx, cy, cx + r * s * math.cos(a), cy + r * s * math.sin(a)], fill=ink, width=3)
for (x0, y0, x1, y1) in [(6, 5, 6, 7), (11, 4.2, 11, 5.8), (4.5, 5, 6, 5)]:
    a, b = P(x0, y0), P(x1, y1)
    d.rectangle([min(a[0], b[0]) - 10, min(a[1], b[1]) - 10, max(a[0], b[0]) + 10, max(a[1], b[1]) + 10], fill=(244, 241, 234))
door(6, 5, 0.9, 0, 90); door(11, 4.2, 0.9, 90, 90); door(4.5, 5, 0.9, 270, 90)
# windows (double lines on outer walls)
for (x0, x1) in [(1.5, 4.5), (7.5, 10), (12.5, 15.5)]:
    a, b = P(x0, 0), P(x1, 0)
    d.rectangle([a[0], a[1] - 14, b[0], a[1] + 14], fill=(244, 241, 234), outline=ink, width=2)
    d.line([a[0], a[1], b[0], b[1]], fill=ink, width=2)
for (y0, y1) in [(7.5, 10.5)]:
    a, b = P(17, y0), P(17, y1)
    d.rectangle([a[0] - 14, a[1], a[0] + 14, b[1]], fill=(244, 241, 234), outline=ink, width=2)
    d.line([a[0], a[1], b[0], b[1]], fill=ink, width=2)
# furniture: bed + bedsides (bedroom top-left)
x, y = P(1.2, 1.2); d.rectangle([x, y, x + 1.9 * s, y + 2.2 * s], outline=ink, width=2)
d.rectangle([x + 0.15 * s, y + 0.1 * s, x + 0.85 * s, y + 0.55 * s], outline=soft, width=2)
d.rectangle([x + 1.05 * s, y + 0.1 * s, x + 1.75 * s, y + 0.55 * s], outline=soft, width=2)
d.line([x, y + 0.9 * s, x + 1.9 * s, y + 0.9 * s], fill=soft, width=2)
# wardrobe
x, y = P(3.6, 0.4); d.rectangle([x, y, x + 0.65 * s, y + 3.6 * s], outline=ink, width=2)
for i in range(1, 6): d.line([x, y + i * 0.6 * s, x + 0.65 * s, y + i * 0.6 * s], fill=soft, width=1)
# living: sofa, armchairs, coffee table, rug
x, y = P(7.0, 8.2); d.rounded_rectangle([x, y, x + 3.0 * s, y + 1.0 * s], 18, outline=ink, width=2)
d.rounded_rectangle([x + 0.2 * s, y + 0.25 * s, x + 2.8 * s, y + 0.95 * s], 12, outline=soft, width=2)
cx, cy = P(8.5, 10.4); d.ellipse([cx - 0.6 * s, cy - 0.6 * s, cx + 0.6 * s, cy + 0.6 * s], outline=ink, width=2)
x, y = P(6.6, 7.8); d.rectangle([x, y, x + 3.8 * s, y + 3.8 * s], outline=faint, width=2)
for ax in (7.0, 9.6):
    x, y = P(ax, 11.0); d.rounded_rectangle([x, y, x + 0.9 * s, y + 0.8 * s], 14, outline=ink, width=2)
# dining table + chairs
x, y = P(12.2, 1.4); d.rectangle([x, y, x + 1.0 * s, y + 2.3 * s], outline=ink, width=2)
for j in range(3):
    for side in (-1, 1):
        cx = x + (0.5 + side * 0.85) * s; cy = y + (0.4 + j * 0.75) * s
        d.rounded_rectangle([cx - 0.24 * s, cy - 0.22 * s, cx + 0.24 * s, cy + 0.22 * s], 8, outline=soft, width=2)
# kitchen run + island
x, y = P(14.2, 7.6); d.rectangle([x, y, x + 2.4 * s, y + 0.65 * s], outline=ink, width=2)
d.ellipse([x + 0.8 * s, y + 0.12 * s, x + 1.2 * s, y + 0.52 * s], outline=soft, width=2)
x, y = P(14.0, 9.6); d.rectangle([x, y, x + 2.4 * s, y + 1.0 * s], outline=ink, width=2)
# bathroom fixtures
cx, cy = P(12.2, 9.5); d.rounded_rectangle([cx - 0.4 * s, cy - 0.85 * s, cx + 0.4 * s, cy + 0.85 * s], 30, outline=ink, width=2)
d.ellipse([P(11.6, 11.2)[0], P(11.6, 11.2)[1], P(12.2, 11.7)[0], P(12.2, 11.7)[1]], outline=soft, width=2)
# dimension lines (ticks, no numbers)
for (x0, x1) in [(0, 6), (6, 11), (11, 17)]:
    a, b = P(x0, -0.9), P(x1, -0.9)
    d.line([a, b], fill=soft, width=2)
    for px in (a[0], b[0]): d.line([px - 10, a[1] + 10, px + 10, a[1] - 10], fill=ink, width=3)
for (y0, y1) in [(0, 5), (5, 12)]:
    a, b = P(-0.9, y0), P(-0.9, y1)
    d.line([a, b], fill=soft, width=2)
    for py in (a[1], b[1]): d.line([a[0] - 10, py + 10, a[0] + 10, py - 10], fill=ink, width=3)
# north arrow
cx, cy = W - 300, 330
d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=ink, width=3)
d.polygon([(cx, cy - 60), (cx + 22, cy + 30), (cx, cy + 10), (cx - 22, cy + 30)], fill=ink)
# pencil sketch strokes over the plan
for i in range(14):
    x = ox + 300 + i * 23
    d.line([x, oy + 760, x + 60, oy + 660], fill=(170, 160, 150), width=1)
im.save(sys.argv[1])
print('plan saved')
