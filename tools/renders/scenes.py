"""Scene definitions for Wellfit Designs illustrative renders.
Run: bvenv/bin/python -I render/scenes.py <scene> <out.png> [scale] [samples]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wf_kit as K  # noqa: E402
from wf_kit import box, cyl, sphere, lathe, wall, arch_shape, cut  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = {}
R = math.radians


def scene(name, w, h):
    def deco(fn):
        SCENES[name] = (fn, w, h)
        return fn
    return deco


def palette():
    return dict(
        plaster=K.mat_plaster('plaster', '#E2D7C6'),
        plaster_warm=K.mat_plaster('plaster_warm', '#E2D2BA', var=0.05),
        plaster_white=K.mat_plaster('plaster_white', '#ECE8E1', var=0.02),
        ceiling=K.mat_plaster('ceiling', '#EEE9E0', var=0.02, bump_s=0.02),
        navy_paint=K.mat_plaster('navy_paint', '#1E3A58', var=0.03, rough=0.85),
        oak=K.mat_oak('oak', axis='Z'),
        oak_x=K.mat_oak('oak_x', axis='X'),
        oak_y=K.mat_oak('oak_y', axis='Y'),
        oak_floor=K.mat_oak_floor('oak_floor'),
        linen=K.mat_fabric('linen', '#D6CAB6'),
        sand=K.mat_fabric('sand', '#CDBFA8'),
        ivory=K.mat_fabric('ivory', '#ECE6DB', weave=420),
        boucle=K.mat_fabric('boucle', '#E6DED0', weave=120, bump_s=0.6, rough=1.0),
        navy=K.mat_fabric('navy', '#1E3754', sheen=0.8, rough=0.85),
        charcoal=K.mat_fabric('charcoal', '#3B3D40', rough=0.9),
        terracotta=K.mat_clay('terracotta', '#B4572F'),
        terracotta_fabric=K.mat_fabric('terracotta_fabric', '#B65A35', sheen=0.6),
        travertine=K.mat_stone('travertine', '#D8C9B1', '#BEAE94'),
        limestone_floor=K.mat_stone('limestone_floor', '#D9CDB8', '#C7B9A2', pore=False,
                                    tiles=(1.2, 0.6), rough=0.42, axis_scale=(1, 5, 1)),
        marble=K.mat_marble('marble'),
        brass=K.mat_brass('brass'),
        black=K.mat_plain('black_steel', '#1B1C1E', rough=0.45, metal=0.6),
        white_top=K.mat_plain('white_top', '#EDEBE6', rough=0.4),
        ceramic=K.mat_plain('ceramic', '#EFEAE2', rough=0.35, coat=0.3),
        wool=K.mat_fabric('wool', '#C4B7A2', weave=160, bump_s=0.4, rough=1.0),
        leaf=K.mat_leaf('leaf', '#5F6B48'),
        olive_leaf=K.mat_leaf('olive_leaf', '#7E8866'),
        bark=K.mat_plain('bark', '#5E5244', rough=0.9),
        glass=K.mat_glass('glass'),
        warm_glow=K.mat_emit('warm_glow', '#FFD3A0', 12),
        lantern=K.mat_emit('lantern', '#FFE2BE', 1.4),
        led=K.mat_emit('led', '#FFC98F', 30),
        concrete=K.mat_concrete('concrete'),
    )


def room(m, x0, x1, y0, y1, h, floor='limestone_floor', walls='plaster', ceiling='ceiling', t=0.25,
         openings=None, skip=()):
    """Closed shell; openings dict keyed by 'back','front','left','right'."""
    o = openings or {}
    box('floor', (x1 - x0 + 2 * t + 0.2, y1 - y0 + 2 * t + 0.2, 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, -0.1), m[floor])
    if 'ceiling' not in skip:
        box('ceiling', (x1 - x0 + 2 * t, y1 - y0 + 2 * t, 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, h + 0.1), m[ceiling])
    W = {}
    if 'back' not in skip:
        W['back'] = wall('wall_back', x0 - t, x1 + t, y1, y1 + t, 0, h, m[walls], o.get('back', ()))
    if 'front' not in skip:
        W['front'] = wall('wall_front', x0 - t, x1 + t, y0 - t, y0, 0, h, m[walls], o.get('front', ()))
    if 'left' not in skip:
        W['left'] = wall('wall_left', x0 - t, x0, y0, y1, 0, h, m[walls], o.get('left', ()))
    if 'right' not in skip:
        W['right'] = wall('wall_right', x1, x1 + t, y0, y1, 0, h, m[walls], o.get('right', ()))
    return W


def mullions(m, axis, fixed, a0, a1, z0, z1, n, mat='black', glass=True, depth=0.08):
    """Window frame along X (axis='x', fixed=y) or Y (axis='y', fixed=x)."""
    step = (a1 - a0) / n
    for i in range(n + 1):
        a = a0 + i * step
        if axis == 'x':
            box('mullion', (0.05, depth, z1 - z0), (a, fixed, (z0 + z1) / 2), m[mat])
        else:
            box('mullion', (depth, 0.05, z1 - z0), (fixed, a, (z0 + z1) / 2), m[mat])
    for z in (z0 + 0.025, z1 - 0.025):
        if axis == 'x':
            box('transom', (a1 - a0, depth, 0.05), ((a0 + a1) / 2, fixed, z), m[mat])
        else:
            box('transom', (depth, a1 - a0, 0.05), (fixed, (a0 + a1) / 2, z), m[mat])
    if glass:
        if axis == 'x':
            box('pane', (a1 - a0, 0.012, z1 - z0), ((a0 + a1) / 2, fixed, (z0 + z1) / 2), m['glass'])
        else:
            box('pane', (0.012, a1 - a0, z1 - z0), (fixed, (a0 + a1) / 2, (z0 + z1) / 2), m['glass'])


def ground_out(m, mat='travertine', size=80, z=-0.02):
    box('ground_out', (size, size, 0.2), (0, 0, z - 0.1), m[mat])


# ===========================================================================
@scene('hero-arched-living-room', 1920, 1080)
def hero(m):
    K.world_sky(sun_elev=26, sun_rot=0, strength=0.22, tint='#FFE6CC')
    K.sun(elev=24, azim=-55, strength=6.0, angle=0.9, color='#FFDDB4')
    box('floor', (14, 22, 0.2), (0, 7, -0.1), m['limestone_floor'])
    box('ceiling', (8.5, 8.4, 0.25), (0, 2.6, 3.725), m['ceiling'])
    wall('front_wall', -4.3, 4.3, -1.6, -1.35, 0, 3.6, m['plaster'])
    bw = wall('back_wall', -4.25, 4.25, 6.5, 6.8, 0, 3.6, m['plaster'],
              openings=[{'kind': 'arch', 'c': -0.7, 'w': 2.5, 'h': 3.05}])
    cut(bw, box('niche_cut', (1.5, 0.3, 1.9), (2.45, 6.5, 1.55)))
    box('niche_shelf', (1.5, 0.2, 0.05), (2.45, 6.62, 1.25), m['oak_x'], bevel=0.004)
    K.vase((2.15, 6.6, 1.275), m['terracotta'], h=0.38, r=0.11, kind=0)
    K.vase((2.62, 6.6, 1.275), m['ceramic'], h=0.24, r=0.09, kind=1)
    K.vase((2.9, 6.58, 1.275), m['terracotta'], h=0.09, r=0.13, kind=2)
    wall('left_wall', -4.3, -4.0, -1.6, 6.8, 0, 3.6, m['plaster'],
         openings=[{'c': 3.3, 'w': 2.2, 'h': 3.0, 'sill': 0.0}])
    for i in range(24):
        box(f'slat{i}', (0.07, 0.04, 3.3), (-3.9, 2.25 + i * 0.092, 1.65), m['oak'], bevel=0.004)
    box('slat_rail', (0.09, 2.3, 0.05), (-3.9, 3.31, 3.32), m['oak_y'])
    wall('right_wall', 4.0, 4.3, -1.6, 6.8, 0, 3.6, m['plaster'])
    for i in range(48):
        box(f'rslat{i}', (0.05, 0.05, 3.6), (3.96, 0.2 + i * 0.13, 1.8), m['oak'], bevel=0.004)
    # courtyard
    wall('court_wall', -9, 6, 12.0, 12.3, 0, 2.6, m['plaster_warm'])
    wall('court_side', -9.3, -9.0, 6.8, 12.3, 0, 2.6, m['plaster_warm'])
    K.tree((-1.0, 9.6, 0), m['bark'], m['olive_leaf'], height=3.1, crown=1.15, n=7000, seed=11, leaf=0.06)
    box('court_bench', (2.2, 0.45, 0.42), (1.8, 11.4, 0.21), m['travertine'], bevel=0.01)
    lathe('court_pot', [(0, 0), (0.32, 0), (0.42, 0.55), (0.4, 0.56), (0.38, 0.5), (0, 0.5)], (-3.0, 10.8, 0),
          m['terracotta'], 48)
    K.foliage((-3.0, 10.8, 0.95), 0.42, 900, m['leaf'], 0.07, 1.0, 21)
    # furniture
    K.rug((0.4, 3.5), (3.6, 2.6), m['wool'])
    K.sofa((2.55, 3.35, 0), length=2.9, depth=1.0, mat=m['linen'], rot=R(90))
    for i, (yy, mm) in enumerate(((2.6, 'terracotta_fabric'), (4.1, 'ivory'))):
        box(f'cushion{i}', (0.14, 0.48, 0.44), (2.75, yy, 0.62), m[mm], bevel=0.06, segs=6, rot=(0, R(-12), 0))
    K.armchair((-1.85, 3.0, 0), m['navy'], rot=R(-110))
    cyl('coffee_table', 0.6, 0.34, (0.55, 3.6, 0.17), m['travertine'], 96, bevel=0.01)
    K.vase((0.42, 3.5, 0.34), m['terracotta'], h=0.44, r=0.13, kind=0)
    box('book', (0.28, 0.21, 0.04), (0.8, 3.75, 0.36), m['ivory'], bevel=0.004, rot=(0, 0, 0.3))
    cyl('side_table', 0.22, 0.48, (-1.7, 4.15, 0.24), m['oak'], 48, bevel=0.006)
    # floor lamp
    cyl('lamp_stem', 0.012, 1.45, (-2.75, 4.2, 0.73), m['brass'], 16)
    cyl('lamp_foot', 0.16, 0.02, (-2.75, 4.2, 0.01), m['brass'], 48)
    sh = lathe('lamp_shade', [(0.24, 0), (0.2, 0.3)], (-2.75, 4.2, 1.3), m['linen'], 48)
    sh.modifiers.new('solid', 'SOLIDIFY').thickness = 0.004
    sphere('lamp_bulb', 0.04, (-2.75, 4.2, 1.42), m['warm_glow'])
    K.point((-2.75, 4.2, 1.42), 25, radius=0.08)
    K.camera((0.35, -0.9, 1.12), (0.1, 6.0, 1.12), lens=24)
    K.area((-0.7, 6.6, 1.6), 2.5, 0, rot=(R(90), 0, 0), size_y=3.1, portal=True)
    K.area((-4.15, 3.3, 1.5), 2.2, 0, rot=(0, R(-90), 0), size_y=3.0, portal=True)
    return dict(exposure=0.3)


# ===========================================================================
@scene('interior-villa-living-room', 1600, 1067)
def villa_living(m):
    K.world_sky(sun_elev=30, strength=0.25, tint='#FFE8D0')
    K.sun(elev=28, azim=35, strength=5.5, angle=1.0, color='#FFE2BC')
    room(m, -3.6, 3.6, -1.4, 6.2, 3.2, floor='oak_floor', openings={
        'back': [{'c': 0.0, 'w': 6.6, 'h': 2.95, 'sill': 0.0}]})
    mullions(m, 'x', 6.32, -3.3, 3.3, 0.0, 2.95, 4)
    # perimeter dropped ceiling with cove LED
    for (sx, sy, cx, cy) in ((7.2, 0.7, 0, -1.05), (7.2, 0.7, 0, 5.85), (0.7, 7.6, -3.25, 2.4), (0.7, 7.6, 3.25, 2.4)):
        box('drop', (sx, sy, 0.3), (cx, cy, 3.05), m['ceiling'])
    for (sx, sy, cx, cy) in ((5.8, 0.03, 0, -0.68), (0.03, 6.2, -2.88, 2.4), (0.03, 6.2, 2.88, 2.4)):
        box('cove', (sx, sy, 0.03), (cx, cy, 3.215), m['led'])
    # outside: pool terrace + garden wall + trees
    ground_out(m, 'travertine')
    box('pool_water', (8, 3.2, 0.02), (0.5, 9.2, -0.03), K.mat_water())
    box('pool_floor', (8, 3.2, 0.1), (0.5, 9.2, -1.0), K.mat_plain('pool_tile', '#9CC3C6', rough=0.3))
    wall('garden_wall', -12, 12, 14.0, 14.3, 0, 2.2, m['plaster_warm'])
    for i, x in enumerate((-6.5, 5.8)):
        K.tree((x, 12.2, 0), m['bark'], m['olive_leaf'], height=3.4, crown=1.3, n=6000, seed=30 + i)
    # built-in oak shelving on the right wall
    box('shelf_back', (0.05, 2.4, 2.6), (3.57, 3.4, 1.3), m['oak'], smooth=False)
    for z in (0.45, 1.05, 1.65, 2.25):
        box('shelf', (0.38, 2.4, 0.04), (3.4, 3.4, z), m['oak_y'])
    for y in (2.2, 4.6):
        box('shelf_side', (0.4, 0.04, 2.6), (3.4, y, 1.3), m['oak'])
    K.vase((3.4, 2.7, 1.07), m['terracotta'], h=0.32, r=0.1, kind=1)
    K.vase((3.4, 3.9, 1.67), m['ceramic'], h=0.26, r=0.1, kind=0)
    K.vase((3.4, 3.2, 0.47), m['terracotta'], h=0.1, r=0.14, kind=2)
    box('books', (0.25, 0.5, 0.24), (3.42, 4.2, 0.59), m['sand'], bevel=0.005)
    # seating
    K.rug((-0.4, 3.0), (3.8, 2.8), m['wool'])
    K.sofa((-2.3, 3.0, 0), length=2.8, depth=1.0, mat=m['linen'], rot=R(-90))
    K.armchair((1.5, 2.2, 0), m['boucle'], rot=R(120))
    K.armchair((1.5, 3.9, 0), m['navy'], rot=R(60))
    lathe('coffee', [(0, 0), (0.5, 0), (0.55, 0.02), (0.55, 0.3), (0.52, 0.33), (0, 0.33)], (-0.4, 3.0, 0),
          m['oak_x'], 64)
    K.vase((-0.5, 3.0, 0.33), m['terracotta'], h=0.12, r=0.16, kind=2)
    box('cushion', (0.46, 0.14, 0.42), (-2.3, 2.3, 0.62), m['terracotta_fabric'], bevel=0.06, segs=6,
        rot=(R(-12), 0, R(-90)))
    K.camera((0.6, -0.5, 1.25), (0.1, 6.2, 1.2), lens=22)
    K.area((0, 6.25, 1.5), 6.6, 0, rot=(R(90), 0, 0), size_y=2.9, portal=True)
    return dict(exposure=0.6)


# ===========================================================================
@scene('interior-villa-bedroom', 1200, 1500)
def bedroom(m):
    K.world_sky(sun_elev=22, strength=0.22, tint='#FFE9D6')
    K.sun(elev=18, azim=105, strength=7.0, angle=1.4, color='#FFE0BA')
    room(m, -2.6, 2.6, -1.0, 5.0, 3.0, floor='oak_floor', openings={
        'right': [{'c': 1.7, 'w': 2.2, 'h': 2.6, 'sill': 0.15}]})
    mullions(m, 'y', 2.72, 0.6, 2.8, 0.15, 2.75, 2)
    ground_out(m, 'plaster_warm', z=-0.3)
    K.tree((6.0, 1.0, -0.3), m['bark'], m['olive_leaf'], height=3.5, crown=1.3, n=5000, seed=9)
    # upholstered headboard wall
    for c in range(6):
        for r in range(2):
            box('panel', (0.56, 0.07, 0.8), (-1.5 + c * 0.6, 4.95, 0.65 + r * 0.82), m['sand'], bevel=0.035, segs=5)
    box('panel_cap', (3.7, 0.12, 0.04), (0, 4.94, 2.08), m['oak_x'])
    # bed
    box('bed_base', (1.86, 2.1, 0.24), (0, 3.85, 0.14), m['oak_x'], bevel=0.01)
    box('mattress', (1.8, 2.04, 0.22), (0, 3.86, 0.37), m['ivory'], bevel=0.05, segs=5)
    box('duvet', (1.98, 1.6, 0.26), (0, 3.5, 0.42), m['ivory'], bevel=0.11, segs=8)
    box('throw', (2.0, 0.5, 0.06), (0, 3.0, 0.56), m['terracotta_fabric'], bevel=0.028, segs=5)
    for sx in (-0.45, 0.45):
        box('pillow', (0.78, 0.2, 0.5), (sx, 4.72, 0.72), m['ivory'], bevel=0.09, segs=6, rot=(R(-18), 0, 0))
        box('pillow2', (0.6, 0.16, 0.38), (sx * 0.95, 4.55, 0.68), m['linen'], bevel=0.07, segs=6, rot=(R(-14), 0, 0))
    for sx in (-1.38, 1.38):
        box('bedside', (0.56, 0.46, 0.5), (sx, 4.68, 0.25), m['oak_x'], bevel=0.008)
        box('bedside_pull', (0.3, 0.01, 0.015), (sx, 4.44, 0.38), m['brass'])
        K.lamp_table((sx, 4.7, 0.5), m['terracotta'] if sx < 0 else m['ceramic'], m['linen'], m['warm_glow'])
        K.point((sx, 4.7, 0.92), 12, radius=0.08)
    K.rug((0, 2.6), (2.9, 2.2), m['wool'])
    box('sheer', (0.02, 0.9, 2.75), (2.5, 1.35, 1.38), K.mat_sheer())
    K.planter((-2.1, 4.3, 0), 0.42, m['terracotta'], m['leaf'], plant_h=1.0, seed=4, n=1400)
    K.camera((-0.55, 0.1, 1.3), (0.15, 5.0, 1.15), lens=24)
    K.area((2.62, 1.9, 1.5), 1.7, 0, rot=(0, R(90), 0), size_y=2.5, portal=True)
    return dict(exposure=1.3)


# ===========================================================================
@scene('interior-villa-kitchen', 1600, 1067)
def kitchen(m):
    K.world_sky(sun_elev=30, strength=0.24, tint='#FFE9D2')
    K.sun(elev=28, azim=-40, strength=5.5, angle=1.0, color='#FFE1BA')
    room(m, -3.2, 3.6, -1.0, 6.0, 3.0, openings={
        'back': [{'c': -1.0, 'w': 2.6, 'h': 1.25, 'sill': 1.15}],
        'left': [{'c': 2.6, 'w': 1.6, 'h': 2.6, 'sill': 0.0}]})
    mullions(m, 'x', 6.12, -2.3, 0.3, 1.15, 2.4, 2)
    mullions(m, 'y', -3.32, 1.8, 3.4, 0.0, 2.6, 1)
    ground_out(m, 'travertine')
    wall('garden_wall', -14, 14, 11.0, 11.3, 0, 2.4, m['plaster_warm'])
    K.tree((-2.0, 9.0, 0), m['bark'], m['olive_leaf'], height=3.2, crown=1.2, n=5000, seed=17)
    K.tree((-8.0, 3.5, 0), m['bark'], m['leaf'], height=3.6, crown=1.4, n=5000, seed=18)
    # base run along back wall
    box('plinth', (4.2, 0.55, 0.1), (-1.1, 5.66, 0.05), m['black'])
    box('base_carcass', (4.2, 0.6, 0.78), (-1.1, 5.69, 0.49), m['oak_x'])
    for i in range(7):
        box('door', (0.596, 0.02, 0.76), (-2.9 + i * 0.6, 5.38, 0.49), m['oak'], bevel=0.002)
    box('counter', (4.24, 0.66, 0.035), (-1.1, 5.66, 0.8975), m['marble'], bevel=0.003)
    box('splash', (4.2, 0.02, 0.24), (-1.1, 5.99, 1.035), m['marble'])
    cyl('tap_post', 0.014, 0.32, (-1.0, 5.8, 1.07), m['brass'], 24)
    box('tap_spout', (0.02, 0.22, 0.02), (-1.0, 5.7, 1.23), m['brass'], bevel=0.008)
    box('sink', (0.6, 0.4, 0.004), (-1.0, 5.6, 0.917), m['black'])
    # open shelf
    for z in (1.45, 1.85):
        box('oshelf', (0.7, 0.26, 0.035), (0.6, 5.86, z), m['oak_x'])
    K.vase((0.42, 5.86, 1.468), m['terracotta'], h=0.24, r=0.08, kind=1)
    K.vase((0.75, 5.86, 1.468), m['ceramic'], h=0.08, r=0.12, kind=2)
    K.vase((0.6, 5.86, 1.868), m['ceramic'], h=0.22, r=0.08, kind=0)
    # tall navy units
    lacquer = K.mat_plain('navy_lacquer', '#1D3550', rough=0.3, coat=0.4)
    box('tall_carcass', (2.4, 0.62, 2.6), (2.4, 5.69, 1.3), lacquer)
    for i in range(4):
        box('tall_door', (0.596, 0.02, 2.55), (1.5 + i * 0.6, 5.37, 1.3), lacquer, bevel=0.002)
        cyl('pull', 0.008, 0.5, (1.5 + i * 0.6 + (0.26 if i % 2 == 0 else -0.26), 5.35, 1.15), m['brass'], 16)
    # island
    box('island_base', (2.6, 0.95, 0.88), (-0.4, 3.2, 0.44), m['oak_x'])
    for i in range(4):
        box('island_door', (0.646, 0.02, 0.84), (-1.375 + i * 0.65, 2.715, 0.46), m['oak'], bevel=0.002)
    box('island_top', (2.7, 1.05, 0.04), (-0.4, 3.2, 0.9), m['marble'], bevel=0.003)
    box('waterfall', (0.04, 1.05, 0.92), (0.97, 3.2, 0.46), m['marble'], bevel=0.003)
    K.vase((-0.9, 3.25, 0.92), m['ceramic'], h=0.12, r=0.18, kind=2)
    for (x, y) in ((-0.95, 3.25), (-0.85, 3.2), (-1.0, 3.15)):
        sphere('fruit', 0.04, (x, y, 0.98), m['terracotta'])
    # stools
    for x in (-1.25, -0.4, 0.45):
        cyl('stool_seat', 0.19, 0.05, (x, 2.4, 0.66), m['oak'], 48, bevel=0.01)
        for a in range(4):
            ang = R(45 + 90 * a)
            cyl('stool_leg', 0.012, 0.64, (x + 0.12 * math.cos(ang), 2.4 + 0.12 * math.sin(ang), 0.32), m['black'], 12)
        lathe('stool_ring', [(0.13, 0.0), (0.14, 0.0), (0.14, 0.012), (0.13, 0.012)], (x, 2.4, 0.22), m['black'], 32)
    # pendants
    for x in (-1.1, 0.3):
        cyl('cord', 0.004, 0.7, (x, 3.2, 2.65), m['black'], 8)
        sphere('globe', 0.15, (x, 3.2, 2.15), K.mat_emit('globe', '#FFE6C8', 5))
        K.point((x, 3.2, 2.15), 18, radius=0.12)
    K.camera((1.0, -0.6, 1.5), (-0.6, 6.0, 1.15), lens=22)
    K.area((-1.0, 6.05, 1.7), 2.4, 0, rot=(R(90), 0, 0), size_y=1.1, portal=True)
    K.area((-3.25, 2.6, 1.3), 1.6, 0, rot=(0, R(-90), 0), size_y=2.6, portal=True)
    return dict(exposure=0.9)


# ===========================================================================
@scene('interior-villa-dining', 1200, 1500)
def dining(m):
    K.world_sky(sun_elev=24, strength=0.22, tint='#FFE6CC')
    K.sun(elev=22, azim=-85, strength=5.5, angle=1.2, color='#FFDDB2')
    W = room(m, -2.6, 2.6, -1.2, 5.4, 3.1, walls='plaster_warm', openings={
        'left': [{'c': 2.5, 'w': 1.8, 'h': 2.6, 'sill': 0.2}]})
    mullions(m, 'y', -2.72, 1.6, 3.4, 0.2, 2.8, 2)
    ground_out(m, 'travertine', z=-0.05)
    K.tree((-6.0, 3.5, 0), m['bark'], m['leaf'], height=3.2, crown=1.3, n=5000, seed=12)
    cut(W['back'], arch_shape('niche', 1.15, 2.0, 0.36, (0, 5.4, 0.85)))
    K.vase((-0.12, 5.47, 0.85), m['terracotta'], h=0.55, r=0.16, kind=0)
    K.vase((0.22, 5.5, 0.85), m['ceramic'], h=0.3, r=0.1, kind=1)
    box('sideboard', (0.45, 2.0, 0.75), (2.37, 2.9, 0.375), m['oak_y'], bevel=0.006)
    for i in range(3):
        box('sb_door', (0.02, 0.664, 0.68), (2.14, 2.233 + i * 0.667, 0.38), m['oak'], bevel=0.002)
    K.vase((2.35, 2.4, 0.75), m['ceramic'], h=0.36, r=0.11, kind=1)
    K.vase((2.35, 3.4, 0.75), m['terracotta'], h=0.1, r=0.15, kind=2)
    K.rug((0, 3.0), (2.6, 3.4), m['wool'])
    box('table_top', (1.0, 2.3, 0.05), (0, 3.0, 0.735), m['oak_y'], bevel=0.006)
    for y in (2.2, 3.8):
        box('table_leg', (0.62, 0.08, 0.71), (0, y, 0.355), m['oak'], bevel=0.004)
    for y in (2.3, 3.0, 3.7):
        K.dining_chair((-0.75, y, 0), m['linen'], m['oak'], rot=R(-90))
        K.dining_chair((0.75, y, 0), m['linen'], m['oak'], rot=R(90))
    K.vase((0.0, 3.0, 0.76), m['terracotta'], h=0.1, r=0.17, kind=2)
    K.vase((0.05, 3.5, 0.76), m['ceramic'], h=0.26, r=0.08, kind=1)
    cyl('cord', 0.004, 0.9, (0, 3.0, 2.65), m['black'], 8)
    sphere('lantern', 0.34, (0, 3.0, 1.9), m['lantern'])
    K.point((0, 3.0, 1.9), 14, radius=0.3)
    box('sheer', (0.02, 1.0, 2.9), (-2.5, 1.7, 1.47), K.mat_sheer())
    K.camera((0.2, 0.05, 1.38), (0.0, 5.4, 1.3), lens=24)
    K.area((-2.62, 2.5, 1.5), 1.8, 0, rot=(0, R(-90), 0), size_y=2.6, portal=True)
    return dict(exposure=0.45)


# ===========================================================================
@scene('interior-villa-bathroom', 1200, 1500)
def bathroom(m):
    K.world_sky(sun_elev=62, strength=0.25, tint='#FFEBD8')
    K.sun(elev=60, azim=20, strength=5.0, angle=1.5, color='#FFE9CF')
    trav_back = K.mat_stone('trav_back', '#D9CAB1', '#C2B196', tiles=(0.6, 1.2), axis_scale=(1, 1, 7), plane='XZ',
                            rough=0.5)
    trav_side = K.mat_stone('trav_side', '#D9CAB1', '#C2B196', tiles=(0.6, 1.2), axis_scale=(1, 1, 7), plane='YZ',
                            rough=0.5)
    floor = K.mat_stone('trav_floor', '#D3C3A8', '#BBAA8E', tiles=(0.6, 0.6), rough=0.45)
    box('floor', (5, 6, 0.2), (0, 1.6, -0.1), floor)
    c = box('ceiling', (4.5, 5.8, 0.2), (0, 1.6, 3.0), m['ceiling'])
    cut(c, box('skylight', (1.0, 1.7, 0.6), (-0.95, 2.5, 3.0)))
    wall('wb', -2.25, 2.25, 4.2, 4.45, 0, 2.9, trav_back)
    wall('wf', -2.25, 2.25, -1.45, -1.2, 0, 2.9, m['plaster_white'])
    wall('wl', -2.25, -2.0, -1.2, 4.2, 0, 2.9, trav_side)
    wall('wr', 2.0, 2.25, -1.2, 4.2, 0, 2.9, m['plaster_white'])
    tub_mat = K.mat_plain('tub', '#F1EDE6', rough=0.3, coat=0.2)
    lathe('tub', [(0, 0.0), (0.62, 0.0), (0.72, 0.08), (0.78, 0.3), (0.8, 0.55), (0.78, 0.585), (0.73, 0.57),
                  (0.69, 0.3), (0.6, 0.15), (0, 0.13)], (-0.95, 2.5, 0), tub_mat, 96, scale=(1.05, 0.5, 1),
          rot=(0, 0, R(90)))
    cyl('filler', 0.018, 1.0, (-0.95, 1.55, 0.5), m['brass'], 24)
    box('filler_spout', (0.02, 0.2, 0.02), (-0.95, 1.64, 0.99), m['brass'], bevel=0.008)
    box('stool', (0.36, 0.36, 0.45), (-1.7, 3.85, 0.225), m['oak_x'], bevel=0.01)
    box('towel', (0.3, 0.3, 0.08), (-1.7, 3.85, 0.49), m['ivory'], bevel=0.03, segs=4)
    # vanity, basin, mirror
    box('vanity', (1.3, 0.5, 0.42), (0.95, 3.95, 0.78), m['oak_x'], bevel=0.006)
    box('vanity_gap', (1.2, 0.005, 0.01), (0.95, 3.699, 0.7), m['black'])
    lathe('basin', [(0, 0), (0.1, 0), (0.17, 0.05), (0.2, 0.14), (0.19, 0.14), (0.16, 0.06), (0, 0.04)],
          (0.95, 3.92, 0.99), m['ceramic'], 64)
    cyl('tap', 0.012, 0.18, (0.95, 4.11, 1.32), m['brass'], 16, rot=(R(90), 0, 0))
    arch_shape('mirror_glow', 0.86, 1.16, 0.01, (0.95, 4.195, 1.37), m['led'])
    arch_shape('mirror', 0.8, 1.1, 0.02, (0.95, 4.18, 1.4), K.mat_mirror())
    K.planter((1.6, 1.3, 0), 0.4, m['terracotta'], m['leaf'], plant_h=1.0, seed=8, n=1500)
    K.camera((0.45, 0.1, 1.35), (0.0, 4.2, 1.3), lens=22)
    K.area((-0.95, 2.5, 2.95), 1.0, 0, rot=(0, 0, 0), size_y=1.7, portal=True)
    return dict(exposure=0.6)


# ===========================================================================
@scene('interior-villa-staircase', 1200, 1500)
def staircase(m):
    K.world_sky(sun_elev=36, strength=0.25, tint='#FFE7CF')
    K.sun(elev=34, azim=100, strength=6.0, angle=0.9, color='#FFE0B8')
    room(m, -2.6, 2.6, -1.6, 5.0, 6.2, openings={
        'right': [{'c': 2.4, 'w': 1.5, 'h': 4.8, 'sill': 0.6}]})
    mullions(m, 'y', 2.72, 1.65, 3.15, 0.6, 5.4, 1)
    ground_out(m, 'travertine', z=-0.05)
    n = 16
    for i in range(n):
        x = -2.3 + i * 0.28 + 0.14
        box('tread', (0.3, 1.05, 0.065), (x, 4.47, (i + 1) * 0.2 - 0.0325), m['oak_x'], bevel=0.004)
    box('landing', (0.8, 1.6, 0.2), (2.2, 4.2, 3.1), m['plaster_white'])
    box('landing_top', (0.8, 1.6, 0.03), (2.2, 4.2, 3.215), m['oak_y'])
    length = math.hypot(4.48, 3.2)
    ang = math.atan2(3.2, 4.48)
    box('handrail_led', (length, 0.012, 0.018), (-0.06, 4.993, 1.0 + 1.6), m['led'], rot=(0, -ang, 0))
    K.tree((-1.45, 2.4, 0.42), m['bark'], m['olive_leaf'], height=2.6, crown=1.0, n=5000, seed=5)
    lathe('big_pot', [(0, 0), (0.42, 0), (0.5, 0.42), (0.48, 0.44), (0, 0.42)], (-1.45, 2.4, 0), m['terracotta'], 48)
    box('bench', (1.4, 0.4, 0.42), (0.5, 4.55, 0.21), m['travertine'], bevel=0.01)
    K.vase((0.2, 4.55, 0.42), m['ceramic'], h=0.3, r=0.1, kind=0)
    K.camera((0.2, -1.2, 1.6), (0.1, 5.0, 1.6), lens=20, shift=(0.0, 0.16))
    K.area((2.62, 2.4, 3.0), 1.5, 0, rot=(0, R(90), 0), size_y=4.8, portal=True)
    return dict(exposure=0.45)


# ===========================================================================
@scene('interior-apartment-living', 1600, 1067)
def apartment(m):
    K.world_sky(sun_elev=9, strength=0.35, tint='#FFE2C4')
    K.sun(elev=9, azim=28, strength=5.0, angle=0.8, color='#FFC98E')
    room(m, -3.0, 3.0, -0.8, 5.5, 2.95, floor='oak_floor', openings={
        'back': [{'c': 0.0, 'w': 5.8, 'h': 2.85, 'sill': 0.05}]})
    mullions(m, 'x', 5.62, -2.9, 2.9, 0.05, 2.9, 4)
    sea = K.mat_plain('sea', '#4E7486', rough=0.12, spec=0.6)
    box('sea', (4000, 4000, 1), (0, 0, -95), sea, smooth=False)
    tw = [K.mat_plain('tw1', '#C9CDCD', rough=0.5), K.mat_plain('tw2', '#D8D0C4', rough=0.6),
          K.mat_plain('tw3', '#B9C2C7', rough=0.35, metal=0.2)]
    K.towers(3, (-1400, 1400), (900, 2800), 34, -95, tw, 80, 320, wmin=60, wmax=140)
    box('balcony', (6.4, 2.0, 0.2), (0, 6.6, -0.1), m['travertine'])
    box('balcony_glass', (6.4, 0.02, 1.05), (0, 7.55, 0.52), m['glass'])
    # media wall on the left
    box('media_back', (0.42, 4.6, 2.95), (-2.79, 2.4, 1.475), m['oak_y'])
    box('niche', (0.02, 2.2, 0.55), (-2.575, 2.4, 1.25), K.mat_plain('niche_dark', '#2B2622', rough=0.7))
    box('niche_led', (0.02, 2.2, 0.012), (-2.57, 2.4, 1.52), m['led'])
    for i in range(6):
        box('media_gap', (0.004, 0.003, 2.95), (-2.578, 0.5 + i * 0.76, 1.475), m['black'])
    K.vase((-2.66, 1.9, 0.975), m['terracotta'], h=0.3, r=0.09, kind=1)
    K.vase((-2.66, 2.6, 0.975), m['ceramic'], h=0.12, r=0.15, kind=2)
    # seating
    K.rug((0.1, 2.6), (3.6, 2.6), m['wool'])
    K.sofa((1.7, 2.6, 0), length=2.7, depth=1.0, mat=m['boucle'], rot=R(90))
    box('cushion', (0.14, 0.48, 0.44), (1.9, 3.3, 0.62), m['terracotta_fabric'], bevel=0.06, segs=6,
        rot=(0, R(-12), 0))
    K.armchair((-1.2, 4.2, 0), m['terracotta_fabric'], rot=R(205))
    K.prism('coffee', K.rounded_rect(1.25, 0.7, 0.3), 0, 0.33, (0.1, 2.6, 0), m['travertine'], bevel=0.008)
    K.vase((0.1, 2.5, 0.33), m['ceramic'], h=0.32, r=0.09, kind=0)
    for x in (-2.8, 2.75):
        box('sheer', (0.4, 0.06, 2.8), (x, 5.38, 1.45), K.mat_sheer(alpha=0.35))
    K.camera((0.7, -0.4, 1.22), (0.2, 5.5, 1.22), lens=22)
    K.area((0, 5.55, 1.45), 5.8, 0, rot=(R(90), 0, 0), size_y=2.85, portal=True)
    return dict(exposure=1.0)


# ===========================================================================
@scene('interior-office-reception', 1600, 1067)
def reception(m):
    K.world_sky(sun_elev=32, strength=0.25, tint='#FFEBD6')
    K.sun(elev=30, azim=118, strength=5.5, angle=1.0, color='#FFE3C0')
    room(m, -4.5, 4.5, -1.2, 7.5, 3.2, floor='concrete', openings={
        'right': [{'c': 3.4, 'w': 6.4, 'h': 2.95, 'sill': 0.05}]}, skip=('left',))
    wall('wall_left', -4.75, -4.5, -1.2, 7.5, 0, 3.2, m['navy_paint'])
    mullions(m, 'y', 4.62, 0.2, 6.6, 0.05, 3.0, 4)
    ground_out(m, 'concrete', z=-0.05)
    tw = [K.mat_plain('tw1', '#B9C0C4', rough=0.2, metal=0.3), K.mat_plain('tw2', '#D6CFC3', rough=0.4)]
    K.towers(5, (90, 500), (-300, 400), 26, -2, tw, 40, 220)
    for i in range(68):
        box('slat', (0.05, 0.06, 3.1), (-4.4 + i * 0.13, 7.44, 1.55), m['oak'], bevel=0.004)
    box('cove_led', (9.0, 0.02, 0.03), (0, 7.38, 3.13), m['led'])
    K.prism('counter', K.stadium(3.2, 0.78), 0, 1.03, (0.4, 5.5, 0), m['travertine'], bevel=0.006)
    K.prism('counter_top', K.stadium(3.34, 0.9), 1.03, 1.075, (0.4, 5.5, 0), m['oak_x'], bevel=0.004)
    K.prism('counter_plinth', K.stadium(3.1, 0.7), 0, 0.06, (0.4, 5.5, 0), m['black'])
    box('desk_back', (3.0, 0.7, 0.74), (0.4, 6.4, 0.37), m['oak_x'])
    K.vase((-0.6, 5.5, 1.075), m['terracotta'], h=0.34, r=0.1, kind=1)
    K.armchair((-3.2, 3.3, 0), m['terracotta_fabric'], rot=R(-120))
    K.armchair((-1.8, 2.3, 0), m['terracotta_fabric'], rot=R(-160))
    cyl('side', 0.26, 0.45, (-2.6, 2.6, 0.225), m['oak'], 48, bevel=0.006)
    K.vase((-2.6, 2.6, 0.45), m['ceramic'], h=0.1, r=0.13, kind=2)
    K.planter((3.7, 6.6, 0), 0.62, m['ceramic'], m['leaf'], plant_h=1.6, seed=7, n=2600)
    K.rug((-2.5, 2.8), (2.6, 2.2), m['wool'])
    for y in (1.2, 3.2):
        box('linear', (4.0, 0.06, 0.04), (0.4, y, 3.12), m['led'])
    K.camera((0.3, 0.1, 1.45), (0.3, 7.5, 1.35), lens=22)
    K.area((4.52, 3.4, 1.5), 6.4, 0, rot=(0, R(90), 0), size_y=2.95, portal=True)
    return dict(exposure=0.35)


# ===========================================================================
@scene('interior-office-workspace', 1600, 1067)
def workspace(m):
    K.world_sky(sun_elev=35, strength=0.28, tint='#FFEBD6')
    K.sun(elev=34, azim=105, strength=5.5, angle=1.0, color='#FFE5C4')
    carpet = K.mat_fabric('carpet', '#8F8A82', weave=220, bump_s=0.5, rough=1.0, sheen=0.1)
    room(m, -7.0, 7.0, -1.2, 13.0, 3.2, floor='concrete', openings={
        'right': [{'c': 3.4, 'w': 6.6, 'h': 2.95, 'sill': 0.05}, {'c': 10.0, 'w': 5.4, 'h': 2.95, 'sill': 0.05}]})
    box('carpet', (11.0, 13.0, 0.01), (-1.0, 5.6, 0.005), carpet, smooth=False)
    mullions(m, 'y', 7.12, 0.1, 6.7, 0.05, 3.0, 4)
    mullions(m, 'y', 7.12, 7.3, 12.7, 0.05, 3.0, 3)
    ground_out(m, 'concrete', z=-30)
    tw = [K.mat_plain('tw1', '#AEB8BE', rough=0.2, metal=0.3), K.mat_plain('tw2', '#D3CCC0', rough=0.4)]
    K.towers(8, (90, 600), (-300, 600), 36, -30, tw, 50, 260)
    felt = [m['sand'], m['sand'], m['terracotta_fabric'], m['sand'], m['navy']]
    rr = random.Random(4)
    for row, y in enumerate((2.6, 5.8, 9.0)):
        box('desk_top', (6.0, 1.5, 0.03), (-1.5, y, 0.745), m['white_top'], bevel=0.003)
        for x in (-4.45, -1.5, 1.45):
            for sy in (-0.6, 0.6):
                box('desk_leg', (0.05, 0.05, 0.73), (x, y + sy, 0.365), m['black'])
        box('screen', (6.0, 0.03, 0.32), (-1.5, y, 0.92), m['sand'], bevel=0.005)
        for i in range(4):
            x = -3.75 + i * 1.5
            K.office_chair((x, y - 1.05, 0), m['charcoal'], m['black'], rot=R(rr.uniform(-15, 15)))
            K.office_chair((x, y + 1.05, 0), m['charcoal'], m['black'], rot=R(180 + rr.uniform(-15, 15)))
            box('mon', (0.55, 0.02, 0.32), (x, y - 0.25, 1.06), m['black'], bevel=0.004)
            box('mon2', (0.55, 0.02, 0.32), (x, y + 0.25, 1.06), m['black'], bevel=0.004)
        K.planter((2.3, y, 0), 0.55, m['oak'], m['leaf'], plant_h=1.0, seed=20 + row, n=1600, round_pot=False)
        box('pendant', (5.4, 0.06, 0.04), (-1.5, y, 2.45), m['led'])
        for x in (-4.0, 1.0):
            cyl('wire', 0.002, 0.73, (x, y, 2.83), m['black'], 6)
    pale = K.mat_fabric('pale_felt', '#E2DACB', weave=140)
    for j in range(14):
        y = 0.6 + j * 0.9
        box('baffle', (11.0, 0.04, 0.32), (-1.0, y, 3.02), m['terracotta_fabric'] if j % 5 == 2 else pale, bevel=0.004)
    box('storage', (0.5, 8.0, 1.1), (-6.7, 5.0, 0.55), m['oak_y'])
    K.camera((-5.8, 0.0, 1.62), (1.5, 11.5, 1.25), lens=20)
    K.area((7.02, 3.4, 1.5), 6.6, 0, rot=(0, R(90), 0), size_y=2.95, portal=True)
    K.area((7.02, 10.0, 1.5), 5.4, 0, rot=(0, R(90), 0), size_y=2.95, portal=True)
    return dict(exposure=0.8)


# ===========================================================================
@scene('interior-meeting-room', 1600, 1067)
def meeting(m):
    K.world_sky(sun_elev=30, strength=0.25, tint='#FFEBD6')
    K.sun(elev=28, azim=100, strength=5.0, angle=1.0, color='#FFE3C0')
    W = room(m, -2.6, 2.6, -1.2, 6.2, 3.0, floor='oak_floor', openings={
        'right': [{'c': 3.0, 'w': 4.0, 'h': 2.3, 'sill': 0.55}]}, skip=('left',))
    mullions(m, 'y', 2.72, 1.0, 5.0, 0.55, 2.85, 2)
    ground_out(m, 'concrete', z=-20)
    tw = [K.mat_plain('tw1', '#AEB8BE', rough=0.2, metal=0.3), K.mat_plain('tw2', '#D3CCC0', rough=0.4)]
    K.towers(11, (80, 500), (-300, 500), 26, -20, tw, 40, 200)
    # glass partition to corridor
    mullions(m, 'y', -2.6, -1.2, 6.2, 0.0, 3.0, 6)
    box('corridor_floor', (2.4, 8.0, 0.2), (-3.8, 2.5, -0.1), m['concrete'])
    wall('corridor_wall', -5.25, -5.0, -1.2, 6.2, 0, 3.0, m['plaster_white'])
    box('corridor_ceiling', (2.6, 8.0, 0.2), (-3.8, 2.5, 3.1), m['ceiling'])
    for y in (0.5, 3.5):
        box('art', (0.03, 1.2, 0.8), (-4.98, y, 1.5), m['terracotta_fabric'] if y < 1 else m['navy'], bevel=0.004)
    K.planter((-4.3, 5.4, 0), 0.5, m['ceramic'], m['leaf'], plant_h=1.2, seed=31, n=1500)
    for i in range(40):
        box('slat', (0.05, 0.06, 2.95), (-2.5 + i * 0.128, 6.17, 1.475), m['oak'], bevel=0.004)
    box('table', (1.2, 3.6, 0.05), (0.1, 3.0, 0.735), m['oak_y'], bevel=0.006)
    for y in (1.6, 4.4):
        box('trestle', (0.9, 0.06, 0.7), (0.1, y, 0.36), m['black'])
    for y in (1.75, 2.58, 3.42, 4.25):
        K.office_chair((-0.72, y, 0), m['charcoal'], m['black'], rot=R(-90))
        K.office_chair((0.92, y, 0), m['charcoal'], m['black'], rot=R(90))
    box('pendant_body', (0.08, 3.0, 0.05), (0.1, 3.0, 2.2), m['black'])
    box('pendant_led', (0.06, 2.96, 0.006), (0.1, 3.0, 2.172), m['led'])
    for y in (1.8, 4.2):
        cyl('wire', 0.002, 0.75, (0.1, y, 2.6), m['black'], 6)
    K.vase((0.1, 3.0, 0.76), m['terracotta'], h=0.12, r=0.15, kind=2)
    K.camera((1.15, -0.4, 1.45), (0.0, 6.2, 1.25), lens=22)
    K.area((2.62, 3.0, 1.7), 4.0, 0, rot=(0, R(90), 0), size_y=2.3, portal=True)
    return dict(exposure=0.3)


# ===========================================================================
@scene('interior-warehouse-facility', 1600, 1067)
def warehouse(m):
    K.world_sky(sun_elev=55, strength=0.3, tint='#FFF0DE')
    K.sun(elev=55, azim=30, strength=5.0, angle=1.0, color='#FFF0DA')
    epoxy = K.mat_plain('epoxy', '#B9B3A8', rough=0.2, coat=0.3)
    panel = K.mat_plaster('panel', '#DDDCD8', var=0.01, bump_s=0.0)
    box('floor', (30, 40, 0.2), (0, 16, -0.1), epoxy)
    roof = box('roof', (28.6, 36, 0.2), (0, 16.5, 9.6), panel)
    for x in (-7.5, 0, 7.5):
        cut(roof, box('sky_cut', (1.6, 26, 1), (x, 18, 9.6)))
    wall('w_left', -14.3, -14.0, -1.5, 34.5, 0, 9.6, panel)
    wall('w_right', 14.0, 14.3, -1.5, 34.5, 0, 9.6, panel)
    wall('w_back', -14.3, 14.3, 34.5, 34.8, 0, 9.6, panel)
    wall('w_front', -14.3, 14.3, -1.8, -1.5, 0, 9.6, panel)
    for y in range(0, 36, 6):
        for x in (-13.75, 13.75):
            box('column', (0.32, 0.32, 9.0), (x, y, 4.5), m['black'])
        box('rafter', (27.8, 0.24, 0.55), (0, y, 9.1), m['black'])
    for x in range(-12, 13, 3):
        box('purlin', (0.12, 36, 0.15), (x, 16.5, 9.42), m['black'])
    navy = K.mat_plain('rack_navy', '#22406A', rough=0.4, metal=0.3)
    orange = K.mat_plain('rack_terracotta', '#C2602F', rough=0.4, metal=0.3)
    card = K.mat_plain('cardboard', '#B8986E', rough=0.85)
    wrap = K.mat_plain('wrap', '#E4E2DE', rough=0.5)
    rr = random.Random(2)
    for rx in (4.6, 8.2, 11.8):
        for y in [6 + 2.7 * i for i in range(10)]:
            for dx in (-0.55, 0.55):
                box('upright', (0.08, 0.08, 6.6), (rx + dx, y, 3.3), navy)
        for lvl in (0.15, 1.75, 3.35, 4.95):
            for dx in (-0.55, 0.55):
                box('beam', (0.06, 24.3, 0.12), (rx + dx, 6 + 12.15, lvl + 0.06), orange)
            for i in range(9):
                y = 6 + 2.7 * i + 1.35
                for k in (-0.65, 0.65):
                    if rr.random() < 0.82:
                        h = rr.uniform(0.7, 1.3)
                        box('load', (1.0, 1.05, h), (rx, y + k * 0.95, lvl + 0.15 + h / 2),
                            rr.choice((card, card, wrap)), bevel=0.01)
    # office pod with mezzanine
    box('pod_floor2', (7.5, 6.5, 0.25), (-10.0, 7.0, 3.3), m['white_top'])
    wall('pod_back', -13.9, -6.3, 9.9, 10.2, 0, 3.2, m['oak_y'])
    wall('pod_side', -6.55, -6.3, 4.0, 10.2, 0, 3.2, m['oak'], openings=[{'c': 7.0, 'w': 4.6, 'h': 2.6, 'sill': 0.3}])
    mullions(m, 'y', -6.42, 4.7, 9.3, 0.3, 2.9, 3)
    wall('pod_front', -13.9, -6.3, 3.75, 4.0, 0, 3.2, m['oak_x'], openings=[{'c': -9.5, 'w': 4.0, 'h': 2.4, 'sill': 0.4}])
    mullions(m, 'x', 3.87, -11.5, -7.5, 0.4, 2.8, 3)
    K.area((-10.0, 7.0, 3.0), 4.0, 400, color='#FFE2B8', size_y=4.0)
    for x in [-13.4 + i * 0.9 for i in range(9)]:
        box('post', (0.04, 0.04, 1.1), (x, 3.85, 4.0), m['black'])
    box('rail', (7.6, 0.05, 0.05), (-10.0, 3.85, 4.55), m['black'])
    box('upper_glass', (7.6, 0.015, 1.0), (-10.0, 3.9, 3.95), m['glass'])
    wall('upper_room', -13.9, -8.0, 6.5, 6.75, 3.42, 6.4, m['plaster_white'], openings=[{'c': -11, 'w': 4, 'h': 2.2, 'sill': 0.4}])
    K.camera((2.8, 0.2, 1.7), (0.5, 34.0, 3.6), lens=18, shift=(0.0, 0.12))
    return dict(exposure=0.15)


# ===========================================================================
@scene('exterior-villa-dusk', 1920, 1080)
def villa_dusk(m):
    K.world_sky(sun_elev=-3.5, sun_rot=0, strength=1.6, air=1.4, dust=2.0)
    K.sun(elev=2, azim=-120, strength=0.0)
    render_white = K.mat_plaster('render', '#EEEAE3', var=0.015, bump_s=0.03)
    trav = K.mat_stone('trav_facade', '#D7C7AC', '#C0AE91', tiles=(1.2, 0.6), axis_scale=(1, 1, 7), plane='XZ', rough=0.6)
    interior = K.mat_emit('interior_glow', '#FFCF95', 7.0)
    gravel = K.mat_concrete('gravel', '#8D8576', rough=0.8)
    box('ground', (120, 120, 0.2), (0, 0, -0.1), gravel)
    # deck around pool
    box('deck', (18, 9, 0.06), (-0.5, -5.5, 0.03), m['travertine'])
    pool_tile = K.mat_emit('pool_glow', '#4FB8C2', 5.0)
    box('pool_floor', (11.0, 3.6, 0.05), (-1.5, -5.6, -0.9), pool_tile)
    box('pool_water', (11.0, 3.6, 0.02), (-1.5, -5.6, 0.0), K.mat_water())
    for (sx, sy, x, y) in ((11.2, 0.1, -1.5, -7.45), (11.2, 0.1, -1.5, -3.75), (0.1, 3.8, -7.05, -5.6), (0.1, 3.8, 4.05, -5.6)):
        box('pool_edge', (sx, sy, 0.95), (x, y, -0.45), K.mat_plain('pool_wall', '#7DB8BD', rough=0.3))
    # ground floor (hollow shell with glazing)
    wall('gf_front', -7.0, 7.0, 0.0, 0.3, 0, 3.4, render_white, openings=[
        {'c': -3.6, 'w': 5.0, 'h': 2.8, 'sill': 0.0}, {'c': 3.4, 'w': 3.6, 'h': 2.8, 'sill': 0.0}])
    mullions(m, 'x', 0.15, -6.1, -1.1, 0.0, 2.8, 3)
    mullions(m, 'x', 0.15, 1.6, 5.2, 0.0, 2.8, 2)
    wall('gf_back', -7.0, 7.0, 9.0, 9.3, 0, 3.4, render_white)
    wall('gf_l', -7.3, -7.0, 0, 9.3, 0, 3.4, render_white)
    wall('gf_r', 7.0, 7.3, 0, 9.3, 0, 3.4, render_white)
    box('gf_inner', (13.8, 0.05, 3.2), (0, 6.0, 1.6), interior)
    box('gf_floor', (14, 9, 0.1), (0, 4.6, 0.05), m['travertine'])
    box('slab1', (15.0, 10.0, 0.35), (0.0, 4.4, 3.575), render_white)
    K.sofa((-3.8, 2.4, 0.1), length=2.8, depth=1.0, mat=m['linen'])
    sphere('ext_pendant', 0.3, (3.3, 2.5, 2.4), m['warm_glow'])
    # first floor cantilever
    wall('ff_front', -5.0, 6.5, -1.3, -1.0, 3.75, 6.9, trav, openings=[{'c': 0.2, 'w': 6.6, 'h': 2.2, 'sill': 0.6}])
    mullions(m, 'x', -1.15, -3.1, 3.5, 4.35, 6.55, 3)
    wall('ff_back', -5.0, 6.5, 8.0, 8.3, 3.75, 6.9, trav)
    wall('ff_l', -5.3, -5.0, -1.3, 8.3, 3.75, 6.9, trav)
    wall('ff_r', 6.5, 6.8, -1.3, 8.3, 3.75, 6.9, trav)
    box('ff_inner', (11.4, 0.05, 2.8), (0.75, 2.0, 5.2), interior)
    box('roof', (12.4, 10.0, 0.3), (0.75, 3.5, 7.05), render_white)
    for i in range(18):
        box('screen_slat', (0.06, 0.12, 2.9), (4.0 + i * 0.12, -1.42, 5.3), m['oak'], bevel=0.004)
    # garden
    for (x, y, s) in ((-11, 2, 41), (10.5, 3, 42), (-13, -6, 43), (12, -8, 44)):
        K.tree((x, y, 0), m['bark'], m['leaf'], height=4.2, crown=1.6, n=4500, seed=s)
    for x in range(-6, 7, 2):
        K.foliage((x, -0.7, 0.35), 0.45, 260, m['leaf'], 0.06, 0.8, x + 70)
    for x in (-6.5, -2.0, 2.5, 6.0):
        K.area((x, -0.6, 0.15), 0.2, 60, color='#FFC98A', rot=(R(-15), 0, 0), spread=60)
    for x in (-3.6, 3.4):
        K.area((x, 1.5, 3.0), 2.5, 500, color='#FFD2A0', rot=(0, 0, 0), size_y=1.5)
    K.area((0.75, 0.5, 6.4), 3.0, 500, color='#FFD2A0', size_y=1.5)
    K.camera((-9.0, -15.0, 1.6), (1.0, 2.0, 3.2), lens=26, shift=(0.0, 0.1))
    return dict(exposure=0.6, look='AgX - Medium High Contrast')


# ===========================================================================
@scene('detail-oak-slat-wall', 1200, 1500)
def slat_detail(m):
    K.world_sky(sun_elev=18, strength=0.3, tint='#FFE9D4')
    K.sun(elev=17, azim=-78, strength=7.0, angle=0.8, color='#FFDDB6')
    room(m, -2.2, 2.2, -1.0, 3.0, 3.0, floor='oak_floor', openings={
        'left': [{'c': 1.4, 'w': 1.6, 'h': 2.5, 'sill': 0.25}]})
    ground_out(m, 'travertine', z=-0.05)
    for i in range(36):
        box('slat', (0.045, 0.06, 2.95), (-1.75 + i * 0.1, 2.94, 1.475), m['oak'], bevel=0.004)
    box('led_slot', (0.02, 0.01, 2.9), (0.55, 2.995, 1.45), K.mat_emit('led_soft', '#FFD2A0', 8))
    box('bench', (1.6, 0.46, 0.4), (0.25, 2.6, 0.24), m['terracotta_fabric'], bevel=0.07, segs=6)
    for x in (-0.45, 0.95):
        box('bench_leg', (0.04, 0.4, 0.05), (x, 2.6, 0.025), m['black'])
    K.vase((-0.25, 2.62, 0.44), m['ceramic'], h=0.32, r=0.1, kind=0)
    box('throw', (0.5, 0.42, 0.05), (0.75, 2.6, 0.465), m['ivory'], bevel=0.02, segs=4)
    K.camera((0.25, -0.2, 1.05), (0.25, 3.0, 1.15), lens=34)
    K.area((-2.22, 1.4, 1.5), 1.6, 0, rot=(0, R(-90), 0), size_y=2.5, portal=True)
    return dict(exposure=0.9)


# ===========================================================================
@scene('detail-custom-wardrobe', 1200, 1500)
def wardrobe(m):
    K.world_sky(sun_elev=25, strength=0.22, tint='#FFE9D2')
    K.sun(elev=24, azim=-70, strength=4.5, angle=1.5, color='#FFE1BA')
    room(m, -2.2, 2.2, -1.2, 3.4, 2.8, openings={'left': [{'c': 0.8, 'w': 1.4, 'h': 2.3, 'sill': 0.3}]})
    ground_out(m, 'travertine', z=-0.05)
    box('carcass_back', (3.0, 0.02, 2.7), (0, 3.39, 1.35), m['oak_x'])
    box('carcass_top', (3.04, 0.62, 0.03), (0, 3.09, 2.685), m['oak_x'])
    box('carcass_plinth', (3.0, 0.55, 0.08), (0, 3.1, 0.04), m['black'])
    for x in (-1.5, -0.9, -0.3, 0.3, 0.9, 1.5):
        box('divider', (0.02, 0.6, 2.62), (x, 3.09, 1.39), m['oak'])
    # bay 4 (0.3..0.9): shelves + folded stacks; bay 5 (0.9..1.5): rail + garments
    for z in (0.62, 1.12, 1.62, 2.12):
        box('shelf', (0.58, 0.56, 0.025), (0.6, 3.1, z), m['oak_x'])
        box('shelf_led', (0.56, 0.008, 0.006), (0.6, 2.84, z - 0.016), m['led'])
    rr = random.Random(6)
    cols = [m['ivory'], m['sand'], m['linen'], m['navy'], m['ivory']]
    for z in (0.635, 1.135, 1.635):
        h = 0.0
        for k in range(rr.randint(3, 5)):
            t = rr.uniform(0.04, 0.07)
            box('fold', (0.36, 0.3, t), (0.6 + rr.uniform(-0.02, 0.02), 3.05, z + h + t / 2), rr.choice(cols),
                bevel=min(0.018, t / 2.2), segs=4)
            h += t
    cyl('rail', 0.012, 0.58, (1.2, 3.12, 2.25), m['brass'], 16, rot=(0, R(90), 0))
    gcols = [m['ivory'], m['sand'], m['navy'], m['linen'], m['terracotta_fabric'], m['ivory']]
    for k in range(7):
        x = 0.98 + k * 0.075
        box('garment', (0.025, 0.46, 0.95 + rr.uniform(-0.1, 0.12)), (x, 3.1, 1.72), gcols[k % len(gcols)],
            bevel=0.01, segs=3)
    box('bay_led', (0.56, 0.008, 0.006), (1.2, 2.84, 2.38), m['led'])
    K.point((0.6, 3.0, 2.35), 6, radius=0.05)
    K.point((1.2, 3.0, 2.4), 6, radius=0.05)
    # doors with fluting
    def door(x_center, open_angle=0.0, hinge=None):
        parts = [box('door', (0.596, 0.022, 2.6), (0, 0, 0), m['oak_x'], bevel=0.002)]
        for f in range(13):
            parts.append(cyl('flute', 0.02, 2.56, (-0.27 + f * 0.045, -0.012, 0), m['oak'], 12))
        pull = cyl('pull', 0.008, 0.45, (0.24, -0.04, 0.0), m['brass'], 16)
        parts.append(pull)
        root = K.bpy.data.objects.new('door_root', None)
        K.link(root)
        for p in parts:
            p.parent = root
        if hinge is None:
            root.location = (x_center, 2.78, 1.39)
        else:
            hx, sign = hinge
            piv = K.bpy.data.objects.new('hinge', None)
            K.link(piv)
            piv.location = (hx, 2.78, 1.39)
            root.parent = piv
            root.location = (-sign * 0.3, 0, 0)
            piv.rotation_euler = (0, 0, R(open_angle))
        return root
    for xc in (-1.2, -0.6, 0.0):
        door(xc)
    door(0.6, open_angle=-105, hinge=(0.3, -1))
    door(1.2, open_angle=105, hinge=(1.5, 1))
    K.camera((-0.1, -0.85, 1.3), (0.35, 3.4, 1.3), lens=30)
    K.area((-2.22, 0.8, 1.45), 1.4, 0, rot=(0, R(-90), 0), size_y=2.3, portal=True)
    return dict(exposure=0.75)


# ===========================================================================
@scene('detail-ceiling-cove-lighting', 1600, 1067)
def ceiling(m):
    K.world_sky(sun_elev=6, strength=0.12, tint='#FFD9B0')
    K.sun(elev=6, azim=80, strength=2.0, angle=1.0, color='#FFC78E')
    room(m, -3.2, 3.2, -3.2, 3.2, 3.6, floor='limestone_floor', openings={
        'right': [{'c': -1.6, 'w': 1.4, 'h': 2.6, 'sill': 0.2}]}, skip=('ceiling',))
    ground_out(m, 'travertine', z=-0.05)
    cove = K.mat_emit('cove_led', '#FFC88E', 45)
    box('slab', (7.0, 7.0, 0.2), (0, 0, 3.7), m['ceiling'])
    w = 0.8
    for (sx, sy, cx, cy) in ((6.4, w, 0, 3.2 - w / 2), (6.4, w, 0, -3.2 + w / 2), (w, 6.4, -3.2 + w / 2, 0),
                             (w, 6.4, 3.2 - w / 2, 0)):
        box('drop1', (sx, sy, 0.35), (cx, cy, 3.425), m['ceiling'])
    i0 = 3.2 - w
    for (sx, sy, cx, cy) in ((2 * i0, 0.03, 0, i0 - 0.06), (2 * i0, 0.03, 0, -i0 + 0.06), (0.03, 2 * i0, -i0 + 0.06, 0),
                             (0.03, 2 * i0, i0 - 0.06, 0)):
        box('cove', (sx, sy, 0.03), (cx, cy, 3.585), cove)
    box('channel', (0.06, 6.4, 0.02), (-2.75, 0, 3.245), m['black'])
    box('channel_led', (0.04, 6.3, 0.005), (-2.75, 0, 3.235), K.mat_emit('ch_led', '#FFD7A8', 18))
    for i in range(46):
        box('slat', (0.05, 0.06, 3.25), (-3.0 + i * 0.13, 3.17, 1.625), m['oak'], bevel=0.004)
    K.pendant((0.6, 0.9, 3.0), m['brass'], m['warm_glow'], r=0.26, drop=0.5, cord_mat=m['black'])
    K.point((0.6, 0.9, 2.75), 30, radius=0.1)
    K.sofa((0.3, 2.4, 0), length=2.6, depth=1.0, mat=m['linen'])
    K.camera((-1.0, -2.7, 1.35), (0.5, 1.6, 3.3), lens=17, two_point=False)
    K.area((3.22, -1.6, 1.5), 1.4, 0, rot=(0, R(90), 0), size_y=2.6, portal=True)
    return dict(exposure=0.4)


# ===========================================================================
@scene('detail-joinery-workbench', 1600, 1067)
def workbench(m):
    K.world_sky(sun_elev=30, strength=0.22, tint='#FFEBD6')
    K.sun(elev=26, azim=-70, strength=4.5, angle=2.0, color='#FFE4C2')
    room(m, -3.5, 3.5, -2.0, 3.0, 3.6, floor='concrete', walls='plaster_white', openings={
        'left': [{'c': 0.2, 'w': 2.6, 'h': 2.2, 'sill': 0.9}]})
    ground_out(m, 'concrete', z=-0.05)
    box('bench_top', (2.2, 0.9, 0.08), (0, 0.4, 0.9), m['oak_x'], bevel=0.006)
    for x in (-0.95, 0.95):
        for y in (0.05, 0.75):
            box('bench_leg', (0.08, 0.08, 0.86), (x, y, 0.43), m['oak'])
        box('bench_stretch', (0.06, 0.7, 0.08), (x, 0.4, 0.2), m['oak'])
    box('bench_shelf', (2.0, 0.7, 0.03), (0, 0.4, 0.2), m['oak_x'])
    box('panel_work', (1.0, 0.6, 0.02), (-0.05, 0.38, 0.95), m['oak_x'], bevel=0.002, rot=(0, 0, R(-6)))
    box('panel_edge', (1.0, 0.6, 0.004), (-0.05, 0.38, 0.9615), K.mat_oak('veneer', '#D2A777', '#9B7046', axis='X'),
        rot=(0, 0, R(-6)))
    box('sanding_block', (0.14, 0.07, 0.035), (0.25, 0.32, 0.98), m['terracotta'], bevel=0.008)
    box('sanding_pad', (0.14, 0.07, 0.006), (0.25, 0.32, 0.962), m['black'])
    box('square_a', (0.3, 0.025, 0.004), (0.62, 0.18, 0.942), K.mat_plain('steel', '#A9ADB0', rough=0.3, metal=1))
    box('square_b', (0.025, 0.18, 0.012), (0.48, 0.255, 0.946), m['oak'])
    cyl('pencil', 0.0045, 0.17, (0.7, 0.45, 0.945), m['black'], 6, rot=(0, R(90), R(25)))
    for (x, yy) in ((-0.62, 0.15), (-0.62, 0.62)):
        box('clamp_bar', (0.02, 0.012, 0.3), (x, yy, 1.02), m['black'])
        box('clamp_jaw', (0.06, 0.03, 0.02), (x - 0.02, yy, 1.16), m['black'])
        cyl('clamp_handle', 0.016, 0.1, (x - 0.02, yy, 0.84), m['terracotta'], 16)
    rr = random.Random(3)
    for i in range(9):
        box('sheet', (0.02, 1.2, 2.2), (-2.6 + i * 0.05, 2.6, 1.12), rr.choice([m['oak'], m['oak'], K.mat_plain('mdf', '#B59D7D', rough=0.8)]),
            rot=(0, R(-8), 0))
    for z in (1.4, 2.0, 2.6):
        box('wshelf', (2.4, 0.3, 0.03), (1.6, 2.83, z), m['oak_x'])
        for k in range(5):
            cyl('jar', 0.05, 0.14, (0.6 + k * 0.45, 2.85, z + 0.085), m['glass'], 24)
    for x in (-0.5, 0.6):
        K.pendant((x, 0.4, 2.2), m['black'], m['warm_glow'], r=0.2, drop=1.4, cord_mat=m['black'])
        K.point((x, 0.4, 2.0), 25, radius=0.1)
    K.camera((0.9, -1.55, 1.75), (0.0, 0.5, 0.95), lens=38, two_point=False, dof=2.15, fstop=4.0)
    K.area((-3.52, 0.2, 2.0), 2.6, 0, rot=(0, R(-90), 0), size_y=2.2, portal=True)
    return dict(exposure=0.35)


# ===========================================================================
@scene('process-design-desk', 1600, 1067)
def design_desk(m):
    K.world_sky(sun_elev=45, strength=0.4, tint='#FFEFDF')
    K.sun(elev=48, azim=-55, strength=4.0, angle=4.0, color='#FFE9CF')
    box('floor', (6, 6, 0.2), (0, 0, -0.1), m['concrete'])
    box('desk', (1.8, 1.1, 0.05), (0, 0, 0.725), m['oak_x'], bevel=0.004)
    plan = K.mat_image('plan', os.path.join(HERE, 'plan.png'), rough=0.85)
    K.plane_uv('plan_sheet', 0.62, 0.44, (-0.06, 0.02, 0.7505), plan, rot=(0, 0, R(-4)))
    K.plane_uv('trace', 0.34, 0.3, (0.2, -0.12, 0.7515), K.mat_sheer('trace', '#F7F5F0', alpha=0.4), rot=(0, 0, R(9)))
    box('trav_sample', (0.16, 0.1, 0.02), (0.38, 0.2, 0.76), m['travertine'], bevel=0.002, rot=(0, 0, R(12)))
    box('marble_sample', (0.12, 0.12, 0.02), (0.42, 0.06, 0.76), m['marble'], bevel=0.002, rot=(0, 0, R(-8)))
    box('oak_sample', (0.22, 0.07, 0.014), (0.36, -0.06, 0.757), m['oak_x'], bevel=0.002, rot=(0, 0, R(-20)))
    box('linen_sample', (0.17, 0.14, 0.004), (-0.43, 0.2, 0.752), m['linen'], bevel=0.001, rot=(0, 0, R(15)))
    box('navy_sample', (0.08, 0.05, 0.004), (-0.42, 0.06, 0.756), m['navy'], rot=(0, 0, R(-10)))
    box('terracotta_tile', (0.1, 0.1, 0.012), (0.44, -0.19, 0.756), m['terracotta'], bevel=0.002, rot=(0, 0, R(24)))
    box('brass_strip', (0.2, 0.02, 0.004), (-0.36, -0.08, 0.752), m['brass'], rot=(0, 0, R(30)))
    cyl('ruler', 0.018, 0.3, (-0.2, -0.22, 0.765), m['white_top'], 3, rot=(0, R(90), R(8)))
    cyl('pencil', 0.0045, 0.17, (0.12, -0.2, 0.755), K.mat_plain('pencil_paint', '#2E2B28', rough=0.4), 6,
        rot=(0, R(90), R(-35)))
    lathe('cup', [(0, 0), (0.035, 0), (0.042, 0.01), (0.045, 0.08), (0.042, 0.08), (0.039, 0.012), (0, 0.012)],
          (-0.42, -0.2, 0.75), m['ceramic'], 48)
    cyl('coffee', 0.039, 0.002, (-0.42, -0.2, 0.815), K.mat_plain('coffee', '#3B2416', rough=0.1), 32)
    K.foliage((0.48, 0.28, 0.77), 0.05, 40, m['olive_leaf'], 0.05, 0.2, 77)
    K.camera((0.0, 0.0, 1.95), (0.0, 0.0, 0.75), lens=40, two_point=False)
    return dict(exposure=0.0)


# ===========================================================================
@scene('process-site-fit-out', 1600, 1067)
def site(m):
    K.world_sky(sun_elev=30, strength=0.3, tint='#FFEFE0')
    K.sun(elev=28, azim=95, strength=4.5, angle=1.5, color='#FFEAD0')
    room(m, -4.0, 4.0, -1.0, 8.0, 3.4, floor='concrete', walls='plaster_white', ceiling='concrete', openings={
        'right': [{'c': 3.5, 'w': 7.0, 'h': 2.6, 'sill': 0.5}]})
    mullions(m, 'y', 4.12, 0.0, 7.0, 0.5, 3.1, 4)
    ground_out(m, 'concrete', z=-12)
    kraft = K.mat_plain('kraft', '#C7AE88', rough=0.9)
    box('protection', (6.0, 5.0, 0.004), (-0.4, 2.2, 0.002), kraft)
    steel = K.mat_plain('galv', '#B7BCC0', rough=0.35, metal=0.8)
    for i in range(10):
        box('stud', (0.05, 0.075, 2.8), (-3.5 + i * 0.6, 5.0, 1.4), steel)
    for z in (0.02, 2.79):
        box('track', (5.6, 0.08, 0.04), (-0.8, 5.0, z), steel)
    gyps = K.mat_plaster('gypsum', '#E3E1DC', var=0.01, bump_s=0.0)
    for x in (-2.9, -1.7):
        box('board', (1.18, 0.0125, 2.4), (x, 4.95, 1.2), gyps)
    box('laser_line', (2.4, 0.002, 0.004), (-2.3, 4.94, 1.15), K.mat_emit('laser', '#FF3020', 25))
    for i in range(7):
        box('runner', (8.0, 0.024, 0.035), (0, i * 1.2, 2.8), K.mat_plain('grid', '#F1F0EC', rough=0.4))
    for j in range(14):
        box('tee', (0.024, 7.2, 0.03), (-3.9 + j * 0.6, 3.6, 2.8), K.mat_plain('grid2', '#F1F0EC', rough=0.4))
    for (x, y) in ((-2.7, 6.6), (-2.1, 6.6), (-2.7, 7.2)):
        box('tile', (0.59, 1.19, 0.015), (x + 0.3, y, 2.81), gyps)
    for x in (-1.5, 1.8):
        cyl('duct', 0.22, 9.0, (x, 3.5, 3.1), steel, 32, rot=(R(90), 0, 0))
    # tripod laser
    for a in range(3):
        ang = R(90 + a * 120)
        box('tripod_leg', (0.02, 0.02, 1.18), (0.4 + 0.18 * math.cos(ang), 2.6 + 0.18 * math.sin(ang), 0.57),
            m['black'], rot=(0.15 * math.sin(ang), -0.15 * math.cos(ang), 0))
    box('laser', (0.12, 0.12, 0.14), (0.4, 2.6, 1.22), m['terracotta'], bevel=0.01)
    # ladder
    alu = K.mat_plain('alu', '#C9CCCE', rough=0.3, metal=1)
    for sx in (-0.22, 0.22):
        box('rail_f', (0.04, 0.07, 2.0), (2.4 + sx, 3.3, 0.98), alu, rot=(R(-10), 0, 0))
        box('rail_b', (0.04, 0.07, 2.0), (2.4 + sx, 3.95, 0.98), alu, rot=(R(10), 0, 0))
    for k in range(6):
        z = 0.3 + k * 0.3
        box('rung', (0.44, 0.04, 0.025), (2.4, 3.27 + z * 0.17, z), alu)
    box('toolbox', (0.5, 0.25, 0.22), (-1.0, 3.0, 0.115), m['black'], bevel=0.01)
    box('toolbox_handle', (0.3, 0.03, 0.03), (-1.0, 3.0, 0.25), m['terracotta'])
    K.camera((-0.6, 0.0, 1.55), (0.3, 8.0, 1.65), lens=22)
    K.area((4.02, 3.5, 1.8), 7.0, 0, rot=(0, R(90), 0), size_y=2.6, portal=True)
    return dict(exposure=0.6)


# ===========================================================================
def material_scene(mat, raking=False, env=False):
    if env:
        K.world_sky(sun_elev=30, strength=0.35, tint='#FFE6C8')
    else:
        K.world_color('#D8D2C8', 0.4)
    if raking:
        K.area((-1.6, -0.2, 0.35), 1.2, 220, color='#FFF1DE', rot=(R(0), R(-78), 0))
    else:
        K.area((-0.8, -0.8, 1.6), 1.6, 160, color='#FFF3E4', rot=(R(40), R(-35), 0))
    K.area((1.2, 1.0, 1.2), 1.0, 25, color='#FFF6EE', rot=(R(-45), R(45), 0))
    box('sample', (1.2, 1.2, 0.02), (0, 0, -0.01), mat, smooth=False)
    cam = K.camera((0, 0, 2.0), (0, 0, 0), lens=50, two_point=False)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 0.62


@scene('material-calacatta-marble', 1024, 1024)
def mat_marble(m):
    material_scene(K.mat_marble('marble_macro', base='#F2EFEA', vein='#7F776B', gold='#B49A6E', rough=0.15,
                                fine=True, scale=2.2))
    return dict(exposure=-0.35)


@scene('material-travertine', 1024, 1024)
def mat_trav(m):
    material_scene(K.mat_stone('trav_macro', '#D6C4A4', '#A68D69', axis_scale=(0.5, 5.0, 1.0), pore_scale=28))
    return dict(exposure=-0.2)


@scene('material-oak', 1024, 1024)
def mat_oak(m):
    material_scene(K.mat_oak_macro('oak_macro'))
    return dict(exposure=-0.4)


@scene('material-linen', 1024, 1024)
def mat_linen(m):
    material_scene(K.mat_fabric('linen_macro', '#D2C4AC', weave=240, bump_s=1.0, slub=True), raking=True)
    return dict(exposure=-0.05)


@scene('material-brushed-brass', 1024, 1024)
def mat_brass(m):
    material_scene(K.mat_brass('brass_macro', rough=0.33, aniso=False), env=True)
    return dict(exposure=-0.1)


# ===========================================================================
def main():
    name = sys.argv[1]
    out = sys.argv[2]
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    samples = int(sys.argv[4]) if len(sys.argv) > 4 else 96
    fn, w, h = SCENES[name]
    K.reset()
    P = palette()
    opts = fn(P) or {}
    K.setup_render(int(w * scale), int(h * scale), samples, exposure=opts.get('exposure', 0.0),
                   look=opts.get('look', 'AgX - Medium High Contrast'))
    K.render(out)


if __name__ == '__main__':
    main()
