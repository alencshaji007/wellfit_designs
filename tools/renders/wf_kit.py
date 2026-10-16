"""Wellfit Designs - procedural architectural render kit for Blender (bpy 5.x).

Builds illustrative interior scenes from primitives with procedural materials,
lit by a physical sky + sun, rendered with Cycles (CPU) + OpenImageDenoise.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Euler

rng = random.Random(7)


# ---------------------------------------------------------------- utilities
def hex2lin(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global rng
    rng = random.Random(7)


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def setup_render(w, h, samples=128, exposure=0.0, look='AgX - Medium High Contrast',
                 bounces=6, clamp=8.0):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    c = s.cycles
    c.device = 'CPU'
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.025
    c.use_denoising = True
    c.denoiser = 'OPENIMAGEDENOISE'
    try:
        c.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        c.denoising_prefilter = 'ACCURATE'
    except Exception:
        pass
    c.max_bounces = bounces
    c.diffuse_bounces = 4
    c.glossy_bounces = 3
    c.transmission_bounces = 8
    c.transparent_max_bounces = 8
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.blur_glossy = 1.0
    c.sample_clamp_indirect = clamp
    s.render.resolution_x = w
    s.render.resolution_y = h
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    s.render.image_settings.color_depth = '8'
    s.view_settings.view_transform = 'AgX'
    try:
        s.view_settings.look = look
    except Exception:
        pass
    s.view_settings.exposure = exposure


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- materials
def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes['Principled BSDF']


def N(nt, kind, **props):
    n = nt.nodes.new(kind)
    for k, v in props.items():
        if k in n.inputs.keys() if hasattr(n.inputs, 'keys') else False:
            n.inputs[k].default_value = v
        else:
            setattr(n, k, v)
    return n


def inp(node, name, value):
    node.inputs[name].default_value = value


def L(nt, a, b):
    nt.links.new(a, b)


def coords(nt, scale=(1, 1, 1), rot=(0, 0, 0), space='Object'):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = scale
    mp.inputs['Rotation'].default_value = rot
    L(nt, tc.outputs[space], mp.inputs['Vector'])
    return mp.outputs['Vector']


def noise(nt, vec, scale=5.0, detail=6.0, rough=0.55, distortion=0.0, dims='3D'):
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.noise_dimensions = dims
    inp(n, 'Scale', scale)
    inp(n, 'Detail', detail)
    inp(n, 'Roughness', rough)
    inp(n, 'Distortion', distortion)
    L(nt, vec, n.inputs['Vector'])
    return n


def ramp(nt, fac, stops):
    r = nt.nodes.new('ShaderNodeValToRGB')
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], stops[0][1]
    els[1].position, els[1].color = stops[-1][0], stops[-1][1]
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = col
    L(nt, fac, r.inputs['Fac'])
    return r


def bump(nt, height, strength=0.1, distance=0.01, normal=None):
    b = nt.nodes.new('ShaderNodeBump')
    inp(b, 'Strength', strength)
    inp(b, 'Distance', distance)
    L(nt, height, b.inputs['Height'])
    if normal is not None:
        L(nt, normal, b.inputs['Normal'])
    return b


def mix_rgb(nt, fac, a, b, blend='MIX'):
    m = nt.nodes.new('ShaderNodeMix')
    m.data_type = 'RGBA'
    m.blend_type = blend
    if isinstance(fac, float):
        m.inputs[0].default_value = fac
    else:
        L(nt, fac, m.inputs[0])
    for idx, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[idx].default_value = v
        else:
            L(nt, v, m.inputs[idx])
    return m.outputs[2]


def mat_plain(name, hexcol, rough=0.6, metal=0.0, spec=0.5, coat=0.0, sheen=0.0):
    m, nt, p = _mat(name)
    inp(p, 'Base Color', hex2lin(hexcol))
    inp(p, 'Roughness', rough)
    inp(p, 'Metallic', metal)
    inp(p, 'Specular IOR Level', spec)
    inp(p, 'Coat Weight', coat)
    inp(p, 'Sheen Weight', sheen)
    return m


def mat_plaster(name='plaster', hexcol='#E8E1D4', var=0.035, rough=0.92, bump_s=0.06):
    m, nt, p = _mat(name)
    v = coords(nt, (1, 1, 1))
    n1 = noise(nt, v, scale=1.6, detail=4, rough=0.5)
    base = hex2lin(hexcol)
    lo = tuple(max(0, c * (1 - var)) for c in base[:3]) + (1,)
    hi = tuple(min(1, c * (1 + var)) for c in base[:3]) + (1,)
    r = ramp(nt, n1.outputs['Fac'], [(0.3, lo), (0.7, hi)])
    L(nt, r.outputs['Color'], p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    inp(p, 'Specular IOR Level', 0.3)
    n2 = noise(nt, v, scale=38, detail=8, rough=0.7)
    b = bump(nt, n2.outputs['Fac'], bump_s, 0.004)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_oak(name='oak', light='#C89B6B', dark='#8E6239', axis='X', rough=0.5,
            scale=1.0, plank=None):
    """Rift-cut oak. Grain runs along `axis`."""
    m, nt, p = _mat(name)
    s = {'X': (0.25, 22, 22), 'Y': (22, 0.25, 22), 'Z': (22, 22, 0.25)}[axis]
    s = tuple(x * scale for x in s)
    v = coords(nt, s)
    n1 = noise(nt, v, scale=1.2, detail=10, rough=0.62, distortion=0.6)
    r = ramp(nt, n1.outputs['Fac'], [(0.25, hex2lin(dark)), (0.55, hex2lin(light)),
                                      (0.8, hex2lin(light))])
    col = r.outputs['Color']
    v2 = coords(nt, tuple(x * 0.08 for x in s))
    n2 = noise(nt, v2, scale=3.0, detail=3)
    col = mix_rgb(nt, 0.18, col, n2.outputs['Color'], 'OVERLAY')
    L(nt, col, p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    inp(p, 'Specular IOR Level', 0.45)
    b = bump(nt, n1.outputs['Fac'], 0.08, 0.002)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


PLANE_ROT = {'XY': (0, 0, 0), 'XZ': (math.pi / 2, 0, 0), 'YZ': (math.pi / 2, math.pi / 2, 0)}


def mat_stone(name='travertine', base='#D9CBB5', vein='#BFAF95', pore=True, tiles=None,
              rough=0.55, axis_scale=(1.0, 7.0, 1.0), joint='#B9AC98', plane='XY', pore_scale=55):
    """Honed travertine / limestone, optional tile joints (tiles=(w, h)). plane: XY floor, XZ / YZ walls."""
    m, nt, p = _mat(name)
    prot = PLANE_ROT[plane]
    v = coords(nt, axis_scale, prot)
    n1 = noise(nt, v, scale=2.2, detail=12, rough=0.62, distortion=0.4)
    r = ramp(nt, n1.outputs['Fac'], [(0.35, hex2lin(vein)), (0.62, hex2lin(base))])
    col = r.outputs['Color']
    if pore:
        vv = coords(nt, (1, 1, 1))
        vor = nt.nodes.new('ShaderNodeTexVoronoi')
        inp(vor, 'Scale', pore_scale)
        L(nt, vv, vor.inputs['Vector'])
        pr = ramp(nt, vor.outputs['Distance'], [(0.0, (0.55, 0.55, 0.55, 1)), (0.12, (1, 1, 1, 1))])
        col = mix_rgb(nt, 0.6, col, pr.outputs['Color'], 'MULTIPLY')
    if tiles:
        vt = coords(nt, (1, 1, 1), prot)
        br = nt.nodes.new('ShaderNodeTexBrick')
        inp(br, 'Scale', 1.0)
        inp(br, 'Mortar Size', 0.0025)
        inp(br, 'Mortar Smooth', 0.2)
        inp(br, 'Brick Width', tiles[0])
        inp(br, 'Row Height', tiles[1])
        br.offset = 0.5
        L(nt, vt, br.inputs['Vector'])
        col = mix_rgb(nt, br.outputs['Fac'], col, hex2lin(joint), 'MIX')
        b = bump(nt, br.outputs['Fac'], 0.25, 0.002)
        b.invert = True
        L(nt, b.outputs['Normal'], p.inputs['Normal'])
    L(nt, col, p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    inp(p, 'Specular IOR Level', 0.4)
    return m


def mat_marble(name='marble', base='#F1EEE9', vein='#8C8478', gold='#B9A27A', rough=0.18, fine=False, scale=0.9):
    m, nt, p = _mat(name)
    v = coords(nt, (scale, scale, scale))
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_type = 'BANDS'
    w.bands_direction = 'DIAGONAL'
    inp(w, 'Scale', 1.0 if fine else 1.3)
    inp(w, 'Distortion', 7 if fine else 14)
    inp(w, 'Detail', 6 if fine else 9)
    inp(w, 'Detail Scale', 1.2 if fine else 1.4)
    inp(w, 'Detail Roughness', 0.5 if fine else 0.62)
    L(nt, v, w.inputs['Vector'])
    if fine:
        r = ramp(nt, w.outputs['Fac'], [(0.0, hex2lin(vein)), (0.008, hex2lin(gold)),
                                         (0.022, hex2lin(base)), (1.0, hex2lin(base))])
    else:
        r = ramp(nt, w.outputs['Fac'], [(0.0, hex2lin(vein)), (0.035, hex2lin(gold)),
                                         (0.09, hex2lin(base)), (1.0, hex2lin(base))])
    n = noise(nt, v, scale=4, detail=10, rough=0.6)
    soft = ramp(nt, n.outputs['Fac'], [(0.3, hex2lin('#E6E1D9')), (0.7, hex2lin(base))])
    col = mix_rgb(nt, 0.5, r.outputs['Color'], soft.outputs['Color'], 'MULTIPLY')
    col2 = mix_rgb(nt, 0.55, r.outputs['Color'], col, 'MIX')
    L(nt, col2, p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    inp(p, 'Coat Weight', 0.2)
    return m


def mat_fabric(name='linen', hexcol='#D8CDBB', rough=0.95, sheen=0.5, weave=380.0, bump_s=0.25, slub=False):
    m, nt, p = _mat(name)
    v = coords(nt, (1, 1, 1))
    w1 = nt.nodes.new('ShaderNodeTexWave')
    w1.bands_direction = 'X'
    inp(w1, 'Scale', weave)
    inp(w1, 'Distortion', 2)
    L(nt, v, w1.inputs['Vector'])
    w2 = nt.nodes.new('ShaderNodeTexWave')
    w2.bands_direction = 'Y'
    inp(w2, 'Scale', weave)
    inp(w2, 'Distortion', 2)
    L(nt, v, w2.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMath')
    mx.operation = 'MULTIPLY'
    L(nt, w1.outputs['Fac'], mx.inputs[0])
    L(nt, w2.outputs['Fac'], mx.inputs[1])
    n = noise(nt, coords(nt, (1, 1, 1) if not slub else (1, 12, 1)), scale=9 if not slub else 6, detail=6)
    base = hex2lin(hexcol)
    r = ramp(nt, n.outputs['Fac'], [(0.3, tuple(c * (0.9 if not slub else 0.92) for c in base[:3]) + (1,)),
                                     (0.7, tuple(min(1, c * 1.06) for c in base[:3]) + (1,))])
    L(nt, r.outputs['Color'], p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    inp(p, 'Sheen Weight', sheen)
    inp(p, 'Specular IOR Level', 0.25)
    b = bump(nt, mx.outputs['Value'], bump_s, 0.0015 if not slub else 0.004)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_brass(name='brass', hexcol='#C9A66B', rough=0.26, brushed=True, aniso=True):
    m, nt, p = _mat(name)
    inp(p, 'Base Color', hex2lin(hexcol))
    inp(p, 'Metallic', 1.0)
    inp(p, 'Roughness', rough)
    if brushed:
        if aniso:
            inp(p, 'Anisotropic', 0.6)
        v = coords(nt, (2, 900, 2))
        n = noise(nt, v, scale=1.0, detail=6)
        b = bump(nt, n.outputs['Fac'], 0.08 if aniso else 0.35, 0.001)
        L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_clay(name='terracotta', hexcol='#B65A33', rough=0.8):
    m, nt, p = _mat(name)
    v = coords(nt, (1, 1, 1))
    n = noise(nt, v, scale=12, detail=8, rough=0.6)
    base = hex2lin(hexcol)
    r = ramp(nt, n.outputs['Fac'], [(0.3, tuple(c * 0.85 for c in base[:3]) + (1,)),
                                     (0.7, tuple(min(1, c * 1.08) for c in base[:3]) + (1,))])
    L(nt, r.outputs['Color'], p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    b = bump(nt, n.outputs['Fac'], 0.12, 0.003)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_glass(name='glass', tint='#F4F7F6', rough=0.0, thin=True):
    m, nt, p = _mat(name)
    inp(p, 'Base Color', hex2lin(tint))
    inp(p, 'Transmission Weight', 1.0)
    inp(p, 'Roughness', rough)
    inp(p, 'IOR', 1.45)
    if thin:
        try:
            inp(p, 'Thin Wall', True)
        except Exception:
            pass
    return m


def mat_emit(name, hexcol='#FFD9A8', strength=8.0):
    m, nt, p = _mat(name)
    inp(p, 'Base Color', hex2lin(hexcol))
    inp(p, 'Emission Color', hex2lin(hexcol))
    inp(p, 'Emission Strength', strength)
    return m


def mat_sheer(name='sheer', hexcol='#F2EDE4', alpha=0.55):
    """Translucent sheer curtain."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = nt.nodes.new('ShaderNodeBsdfTranslucent')
    tr.inputs['Color'].default_value = hex2lin(hexcol)
    df = nt.nodes.new('ShaderNodeBsdfDiffuse')
    df.inputs['Color'].default_value = hex2lin(hexcol)
    tp = nt.nodes.new('ShaderNodeBsdfTransparent')
    m1 = nt.nodes.new('ShaderNodeMixShader')
    m1.inputs[0].default_value = 0.5
    L(nt, df.outputs[0], m1.inputs[1])
    L(nt, tr.outputs[0], m1.inputs[2])
    m2 = nt.nodes.new('ShaderNodeMixShader')
    m2.inputs[0].default_value = alpha
    L(nt, tp.outputs[0], m2.inputs[1])
    L(nt, m1.outputs[0], m2.inputs[2])
    L(nt, m2.outputs[0], out.inputs['Surface'])
    return m


def mat_leaf(name='leaf', hexcol='#5E6B45'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    inp(p, 'Base Color', hex2lin(hexcol))
    inp(p, 'Roughness', 0.55)
    inp(p, 'Subsurface Weight', 0.15)
    return m


def mat_water(name='water'):
    m, nt, p = _mat(name)
    inp(p, 'Base Color', hex2lin('#7FA9B5'))
    inp(p, 'Transmission Weight', 1.0)
    inp(p, 'Roughness', 0.02)
    inp(p, 'IOR', 1.33)
    v = coords(nt, (1, 1, 1))
    n = noise(nt, v, scale=3.0, detail=4)
    b = bump(nt, n.outputs['Fac'], 0.12, 0.02)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


# ---------------------------------------------------------------- geometry
def _finish(obj, mat=None, bevel=0.0, segs=3, subsurf=0, smooth=True):
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel > 0:
        b = obj.modifiers.new('bevel', 'BEVEL')
        b.width = bevel
        b.segments = segs
        b.limit_method = 'ANGLE'
        b.harden_normals = False
    if subsurf:
        s = obj.modifiers.new('subd', 'SUBSURF')
        s.levels = subsurf
        s.render_levels = subsurf
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
        try:
            obj.data.set_sharp_from_angle(angle=math.radians(35))
        except Exception:
            pass
    return obj


def box(name, size, loc, mat=None, bevel=0.0, segs=3, rot=(0, 0, 0), subsurf=0, smooth=None):
    """size = full extents (x, y, z); loc = centre."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj)
    return _finish(obj, mat, bevel, segs, subsurf, smooth=(bevel > 0 or subsurf > 0) if smooth is None else smooth)


def cyl(name, r, h, loc, mat=None, verts=64, rot=(0, 0, 0), bevel=0.0, r2=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj)
    _finish(obj, mat, bevel, 3, 0, smooth=True)
    return obj


def sphere(name, r, loc, mat=None, scale=(1, 1, 1), segs=48, rings=24):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.scale = scale
    link(obj)
    return _finish(obj, mat, smooth=True)


def lathe(name, profile, loc, mat=None, segs=64, scale=(1, 1, 1), rot=(0, 0, 0), close_top=False):
    """profile: list of (radius, z) from bottom to top. Builds a solid of revolution."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for a_ring, b_ring in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
    if profile[0][0] > 0:
        bm.faces.new(list(reversed(rings[0])))
    if close_top and profile[-1][0] > 0:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.scale = scale
    obj.rotation_euler = rot
    link(obj)
    return _finish(obj, mat, smooth=True)


def arch_shape(name, w, h, depth, loc, mat=None, rot=(0, 0, 0), segs=48):
    """Solid arch prism (rectangle with semicircular top). Arch faces +/-Y, centred on x."""
    r = w / 2
    pts = [(-r, 0), (r, 0), (r, h - r)]
    for i in range(1, segs):
        a = math.pi * i / segs
        pts.append((r * math.cos(a), h - r + r * math.sin(a)))
    pts.append((-r, h - r))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    front = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    back = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], back[i], back[j], front[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def cut(target, cutter, hide=True, solver='EXACT'):
    mod = target.modifiers.new('cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = solver
    if hide:
        cutter.hide_render = True
        cutter.hide_viewport = True
    # boolean should come before bevel
    if len(target.modifiers) > 1:
        target.modifiers.move(len(target.modifiers) - 1, 0)
    return mod


def wall(name, x0, x1, y0, y1, z0, z1, mat, openings=()):
    """Axis aligned wall block; openings: list of dicts {kind: 'rect'|'arch', c: centre along wall,
    w, h, sill}. Wall runs along X if (x1-x0) > (y1-y0) else along Y."""
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    w = box(name, (sx, sy, sz), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat)
    along_x = sx >= sy
    for i, o in enumerate(openings):
        thick = (sy if along_x else sx) + 0.2
        if o.get('kind', 'rect') == 'arch':
            if along_x:
                c = arch_shape(f'{name}_cut{i}', o['w'], o['h'], thick,
                               (o['c'], (y0 + y1) / 2, z0 + o.get('sill', 0)))
            else:
                c = arch_shape(f'{name}_cut{i}', o['w'], o['h'], thick,
                               ((x0 + x1) / 2, o['c'], z0 + o.get('sill', 0)), rot=(0, 0, math.pi / 2))
        else:
            if along_x:
                c = box(f'{name}_cut{i}', (o['w'], thick, o['h']),
                        (o['c'], (y0 + y1) / 2, z0 + o.get('sill', 0) + o['h'] / 2))
            else:
                c = box(f'{name}_cut{i}', (thick, o['w'], o['h']),
                        ((x0 + x1) / 2, o['c'], z0 + o.get('sill', 0) + o['h'] / 2))
        cut(w, c)
    return w


def join(objs, name):
    ctx = bpy.context
    for o in ctx.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    ctx.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


# ---------------------------------------------------------------- furniture
def sofa(loc, length=2.6, depth=0.98, mat=None, rot=0.0, seat_h=0.40, arms=True, cushions=3,
         plinth_mat=None):
    x, y, z = loc
    parts = []
    base_h = 0.16
    pm = plinth_mat or mat
    parts.append(box('sofa_base', (length - 0.06, depth - 0.06, base_h), (0, 0, base_h / 2 + 0.03), pm, bevel=0.02))
    seat_t = seat_h - base_h - 0.03
    arm_w = 0.2 if arms else 0.0
    inner = length - 2 * arm_w
    cw = inner / cushions
    for i in range(cushions):
        cx = -inner / 2 + cw * (i + 0.5)
        parts.append(box(f'seat{i}', (cw - 0.012, depth - 0.24, seat_t), (cx, 0.1, base_h + 0.03 + seat_t / 2),
                         mat, bevel=0.06, segs=6))
        parts.append(box(f'back{i}', (cw - 0.02, 0.24, 0.42), (cx, -depth / 2 + 0.17, seat_h + 0.17),
                         mat, bevel=0.08, segs=6, rot=(math.radians(-8), 0, 0)))
    parts.append(box('backframe', (length - 0.12, 0.16, seat_h + 0.12), (0, -depth / 2 + 0.09, (seat_h + 0.12) / 2 + 0.03),
                     mat, bevel=0.05, segs=5))
    if arms:
        for sgn in (-1, 1):
            parts.append(box('arm', (arm_w, depth, seat_h + 0.16), (sgn * (length / 2 - arm_w / 2), 0, (seat_h + 0.16) / 2 + 0.03),
                             mat, bevel=0.07, segs=6))
    root = bpy.data.objects.new('sofa', None)
    link(root)
    for p in parts:
        p.parent = root
    root.location = (x, y, z)
    root.rotation_euler = (0, 0, rot)
    return root


def armchair(loc, mat, rot=0.0, w=0.86, d=0.86, legs_mat=None):
    root = bpy.data.objects.new('armchair', None)
    link(root)
    parts = [
        box('ac_seat', (w - 0.24, d - 0.2, 0.18), (0, 0.06, 0.34), mat, bevel=0.06, segs=6),
        box('ac_back', (w, 0.2, 0.74), (0, -d / 2 + 0.1, 0.4), mat, bevel=0.08, segs=6),
        box('ac_arm_l', (0.16, d, 0.56), (-w / 2 + 0.08, 0, 0.31), mat, bevel=0.07, segs=6),
        box('ac_arm_r', (0.16, d, 0.56), (w / 2 - 0.08, 0, 0.31), mat, bevel=0.07, segs=6),
        box('ac_base', (w, d, 0.2), (0, 0, 0.14), mat, bevel=0.05, segs=5),
    ]
    if legs_mat:
        for sx in (-1, 1):
            for sy in (-1, 1):
                parts.append(cyl('ac_leg', 0.018, 0.05, (sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), 0.025), legs_mat, 16))
    for p in parts:
        p.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    return root


def dining_chair(loc, seat_mat, frame_mat, rot=0.0):
    root = bpy.data.objects.new('chair', None)
    link(root)
    parts = [box('ch_seat', (0.48, 0.46, 0.07), (0, 0, 0.45), seat_mat, bevel=0.03, segs=5)]
    back = box('ch_back', (0.5, 0.06, 0.34), (0, -0.21, 0.72), seat_mat, bevel=0.025, segs=5)
    bend = back.modifiers.new('bend', 'SIMPLE_DEFORM')
    bend.deform_method = 'BEND'
    bend.deform_axis = 'Z'
    bend.angle = math.radians(-50)
    back.modifiers.move(len(back.modifiers) - 1, 0)
    sub = back.modifiers.new('sub', 'SUBSURF')
    sub.levels = 0
    parts.append(back)
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box('ch_leg', (0.032, 0.032, 0.43), (sx * 0.2, sy * 0.19, 0.215), frame_mat, bevel=0.006))
    for sx in (-1, 1):
        parts.append(box('ch_post', (0.03, 0.03, 0.3), (sx * 0.21, -0.215, 0.6), frame_mat, bevel=0.006))
    for p in parts:
        p.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    return root


def office_chair(loc, fabric, dark, rot=0.0):
    root = bpy.data.objects.new('ochair', None)
    link(root)
    parts = [box('oc_seat', (0.5, 0.48, 0.08), (0, 0, 0.47), fabric, bevel=0.03, segs=4),
             box('oc_back', (0.46, 0.05, 0.52), (0, -0.25, 0.8), fabric, bevel=0.025, segs=4,
                 rot=(math.radians(-10), 0, 0)),
             cyl('oc_col', 0.022, 0.36, (0, 0, 0.26), dark, 24)]
    for i in range(5):
        a = 2 * math.pi * i / 5
        leg = box('oc_leg', (0.3, 0.035, 0.03), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.07), dark, bevel=0.008,
                  rot=(0, 0, a))
        parts.append(leg)
        parts.append(sphere('oc_wheel', 0.025, (0.29 * math.cos(a), 0.29 * math.sin(a), 0.025), dark))
    for sx in (-1, 1):
        parts.append(box('oc_arm', (0.04, 0.3, 0.025), (sx * 0.27, -0.02, 0.66), dark, bevel=0.008))
        parts.append(box('oc_armpost', (0.025, 0.025, 0.18), (sx * 0.27, -0.1, 0.57), dark))
    for p in parts:
        p.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    return root


def vase(loc, mat, h=0.42, r=0.13, kind=0, rot=0.0):
    if kind == 0:   # amphora
        prof = [(0.0, 0), (r * 0.55, 0), (r * 0.9, h * 0.15), (r, h * 0.4), (r * 0.82, h * 0.68),
                (r * 0.36, h * 0.86), (r * 0.32, h * 0.97), (r * 0.38, h), (r * 0.3, h), (r * 0.26, h * 0.9)]
    elif kind == 1:  # bottle
        prof = [(0.0, 0), (r * 0.7, 0), (r, h * 0.08), (r, h * 0.55), (r * 0.6, h * 0.72),
                (r * 0.25, h * 0.8), (r * 0.25, h), (r * 0.18, h), (r * 0.18, h * 0.85)]
    else:            # bowl
        prof = [(0.0, 0), (r * 0.45, 0), (r * 0.8, h * 0.35), (r, h), (r * 0.94, h), (r * 0.74, h * 0.38), (0.0, h * 0.12)]
    return lathe('vase', prof, loc, mat, 64, rot=(0, 0, rot))


def pendant(loc, shell_mat, glow_mat, r=0.22, drop=0.9, cord_mat=None, kind='dome'):
    x, y, z = loc
    parts = []
    if kind == 'dome':
        prof = [(0.02, 0.0), (r * 0.25, 0.0)] + [
            (r * math.sin(math.radians(a)), -r * (1 - math.cos(math.radians(a))) * 0.9 + 0.0) for a in range(15, 91, 5)]
        prof = [(p[0], p[1]) for p in prof]
        # build as thin shell: outer only (open bottom), flip sign so it hangs
        shell = lathe('pendant_shell', [(r, -r * 0.72), (r * 0.98, -r * 0.6), (r * 0.85, -r * 0.35),
                                         (r * 0.55, -r * 0.12), (r * 0.2, -0.01), (0.0, 0.0)],
                      (x, y, z), shell_mat, 64)
        shell.modifiers.new('solid', 'SOLIDIFY').thickness = 0.006
        parts.append(shell)
        parts.append(sphere('bulb', r * 0.18, (x, y, z - r * 0.45), glow_mat))
    elif kind == 'globe':
        parts.append(sphere('globe', r, (x, y, z - r), glow_mat))
    if cord_mat:
        parts.append(cyl('cord', 0.004, drop, (x, y, z + drop / 2), cord_mat, 8))
    return parts


def rug(loc, size, mat, rot=0.0):
    return box('rug', (size[0], size[1], 0.012), (loc[0], loc[1], 0.006), mat, bevel=0.004, rot=(0, 0, rot))


def foliage(center, radius, n, mat, leaf=0.05, squash=0.75, seed=1, spread=(1, 1, 1)):
    """Cloud of small leaves (folded diamonds) built in one pass, returned as one mesh."""
    from mathutils import Matrix
    r = random.Random(seed)
    verts, faces = [], []
    for i in range(n):
        u, v = r.random(), r.random()
        th, ph = 2 * math.pi * u, math.acos(2 * v - 1)
        rr = radius * (r.random() ** 0.45)
        p = Vector((rr * math.sin(ph) * math.cos(th) * spread[0], rr * math.sin(ph) * math.sin(th) * spread[1],
                    rr * math.cos(ph) * squash * spread[2]))
        sc = leaf * (0.7 + 0.6 * r.random())
        rot = Euler((r.uniform(-1.3, 1.3), r.uniform(-1.3, 1.3), r.uniform(0, 6.28))).to_matrix()
        tmpl = ((0, -0.5, 0), (0.17, 0, 0.05), (0, 0.5, 0), (-0.17, 0, 0.05))
        b = len(verts)
        for (x, y, z) in tmpl:
            verts.append(tuple(rot @ Vector((x * sc, y * sc, z * sc)) + p))
        faces.append((b, b + 1, b + 2))
        faces.append((b, b + 2, b + 3))
    me = bpy.data.meshes.new('leaves')
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new('leaves', me)
    obj.location = center
    link(obj)
    obj.data.materials.append(mat)
    return obj


def tree(loc, trunk_mat, leaf_mat, height=2.4, crown=0.75, n=2600, seed=3, leaf=0.055, branches=4):
    r = random.Random(seed)
    x, y, z = loc
    objs = [cyl('trunk', 0.06, height * 0.55, (x, y, z + height * 0.275), trunk_mat, 16,
                rot=(r.uniform(-0.08, 0.08), r.uniform(-0.08, 0.08), 0))]
    for b in range(branches):
        a = 2 * math.pi * b / branches + r.uniform(-0.3, 0.3)
        lean = r.uniform(0.35, 0.6)
        ln = height * r.uniform(0.28, 0.38)
        bx, by = x + math.cos(a) * ln * math.sin(lean) / 2, y + math.sin(a) * ln * math.sin(lean) / 2
        objs.append(cyl('branch', 0.03, ln, (bx, by, z + height * 0.5 + ln * 0.4), trunk_mat, 12,
                        rot=(-math.sin(a) * lean, math.cos(a) * lean, 0)))
        cx = x + math.cos(a) * crown * 0.55
        cy = y + math.sin(a) * crown * 0.55
        objs.append(foliage((cx, cy, z + height * 0.78 + r.uniform(-0.1, 0.15)), crown * 0.62, n // branches, leaf_mat,
                            leaf, 0.7, seed + b))
    objs.append(foliage((x, y, z + height * 0.9), crown * 0.7, n // 3, leaf_mat, leaf, 0.6, seed + 99))
    return objs


def planter(loc, size, pot_mat, leaf_mat, plant_h=0.8, seed=5, n=900, round_pot=True):
    x, y, z = loc
    objs = []
    if round_pot:
        objs.append(lathe('pot', [(0, 0), (size * 0.4, 0), (size * 0.5, size * 0.9), (size * 0.48, size * 0.92),
                                  (size * 0.46, size * 0.85), (0, size * 0.85)], (x, y, z), pot_mat, 48))
    else:
        objs.append(box('pot', (size, size, size * 0.9), (x, y, z + size * 0.45), pot_mat, bevel=0.01))
    objs.append(foliage((x, y, z + size * 0.9 + plant_h * 0.45), plant_h * 0.5, n, leaf_mat, 0.07, 1.0, seed,
                        spread=(1, 1, 1.25)))
    return objs


# ---------------------------------------------------------------- lighting / camera
def world_sky(sun_elev=25, sun_rot=210, strength=1.0, kind='MULTIPLE_SCATTERING', disc=False,
              air=1.0, dust=1.0, ozone=1.0, tint=None):
    w = bpy.data.worlds.new('world')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = kind
    sky.sun_disc = disc
    sky.sun_elevation = math.radians(sun_elev)
    sky.sun_rotation = math.radians(sun_rot)
    try:
        sky.air_density = air
        sky.aerosol_density = dust
        sky.ozone_density = ozone
    except Exception:
        pass
    if tint:
        mx = nt.nodes.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1.0
        L(nt, sky.outputs['Color'], mx.inputs[6])
        mx.inputs[7].default_value = hex2lin(tint)
        L(nt, mx.outputs[2], bg.inputs['Color'])
    else:
        L(nt, sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    return w


def world_color(hexcol='#DCE3E8', strength=1.0):
    w = bpy.data.worlds.new('world')
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = hex2lin(hexcol)
    bg.inputs['Strength'].default_value = strength
    return w


def sun(elev=25, azim=210, strength=4.0, angle=1.2, color='#FFF1DE'):
    """azim: compass direction the light comes FROM (deg, 0=+Y, 90=+X)."""
    ld = bpy.data.lights.new('sun', 'SUN')
    ld.energy = strength
    ld.angle = math.radians(angle)
    ld.color = hex2lin(color)[:3]
    o = bpy.data.objects.new('sun', ld)
    link(o)
    # light points along -Z; rotate so it travels from (azim, elev) toward origin
    d = Vector((math.sin(math.radians(azim)) * math.cos(math.radians(elev)),
                math.cos(math.radians(azim)) * math.cos(math.radians(elev)),
                math.sin(math.radians(elev))))
    o.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    return o


def area(loc, size, strength, color='#FFE7C7', rot=(0, 0, 0), size_y=None, portal=False, spread=180):
    ld = bpy.data.lights.new('area', 'AREA')
    ld.energy = strength
    ld.color = hex2lin(color)[:3]
    if size_y:
        ld.shape = 'RECTANGLE'
        ld.size = size
        ld.size_y = size_y
    else:
        ld.size = size
    ld.spread = math.radians(spread)
    if portal:
        ld.cycles.is_portal = True
    o = bpy.data.objects.new('area', ld)
    o.location = loc
    o.rotation_euler = rot
    link(o)
    return o


def point(loc, strength, color='#FFD7A3', radius=0.05):
    ld = bpy.data.lights.new('pt', 'POINT')
    ld.energy = strength
    ld.color = hex2lin(color)[:3]
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new('pt', ld)
    o.location = loc
    link(o)
    return o


def camera(loc, target, lens=28, shift=(0.0, 0.0), dof=None, fstop=5.6, two_point=True):
    cd = bpy.data.cameras.new('cam')
    cd.lens = lens
    cd.sensor_width = 36
    cd.shift_x, cd.shift_y = shift
    cam = bpy.data.objects.new('cam', cd)
    link(cam)
    cam.location = loc
    d = Vector(target) - Vector(loc)
    if two_point:
        yaw = math.atan2(d.y, d.x) - math.pi / 2
        cam.rotation_euler = (math.radians(90), 0, yaw)
    else:
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------- extra helpers
def prism(name, outline, z0, z1, loc=(0, 0, 0), mat=None, rot=(0, 0, 0), bevel=0.0, segs=3):
    """Extrude a 2D outline (list of (x, y), CCW) between z0 and z1."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in outline]
    top = [bm.verts.new((x, y, z1)) for x, y in outline]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj)
    return _finish(obj, mat, bevel, segs, 0, smooth=bevel > 0)


def stadium(length, width, segs=24):
    r = width / 2
    hl = length / 2 - r
    pts = []
    for i in range(segs + 1):
        a = -math.pi / 2 + math.pi * i / segs
        pts.append((hl + r * math.cos(a), r * math.sin(a)))
    for i in range(segs + 1):
        a = math.pi / 2 + math.pi * i / segs
        pts.append((-hl + r * math.cos(a), r * math.sin(a)))
    return pts


def rounded_rect(w, d, r, segs=8):
    pts = []
    corners = ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180),
               (w / 2 - r, -d / 2 + r, 270))
    for cx, cy, a0 in corners:
        for i in range(segs + 1):
            a = math.radians(a0 + 90 * i / segs)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def mat_concrete(name='concrete', hexcol='#BDB5AA', rough=0.35):
    m, nt, p = _mat(name)
    v = coords(nt, (1, 1, 1))
    n1 = noise(nt, v, scale=1.2, detail=10, rough=0.62)
    base = hex2lin(hexcol)
    r = ramp(nt, n1.outputs['Fac'], [(0.3, tuple(c * 0.86 for c in base[:3]) + (1,)),
                                     (0.7, tuple(min(1, c * 1.08) for c in base[:3]) + (1,))])
    L(nt, r.outputs['Color'], p.inputs['Base Color'])
    n2 = noise(nt, v, scale=7, detail=6)
    rr = ramp(nt, n2.outputs['Fac'], [(0.3, (rough * 0.7,) * 3 + (1,)), (0.7, (rough * 1.4,) * 3 + (1,))])
    L(nt, rr.outputs['Color'], p.inputs['Roughness'])
    return m


def mat_oak_floor(name='oak_floor', light='#C59B6E', dark='#8F6640', plank=(1.6, 0.19), rough=0.42):
    m, nt, p = _mat(name)
    v = coords(nt, (1, 1, 1))
    br = nt.nodes.new('ShaderNodeTexBrick')
    inp(br, 'Scale', 1.0)
    inp(br, 'Mortar Size', 0.0016)
    inp(br, 'Brick Width', plank[0])
    inp(br, 'Row Height', plank[1])
    br.offset = 0.37
    br.offset_frequency = 1
    L(nt, v, br.inputs['Vector'])
    inp(br, 'Color1', (1, 1, 1, 1))
    inp(br, 'Color2', (0.55, 0.55, 0.55, 1))
    vg = coords(nt, (0.3, 26, 26))
    n1 = noise(nt, vg, scale=1.3, detail=10, rough=0.62, distortion=0.6)
    r = ramp(nt, n1.outputs['Fac'], [(0.25, hex2lin(dark)), (0.6, hex2lin(light))])
    col = mix_rgb(nt, 0.35, r.outputs['Color'], br.outputs['Color'], 'MULTIPLY')
    col = mix_rgb(nt, br.outputs['Fac'], col, hex2lin('#4A3826'), 'MIX')
    L(nt, col, p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    b = bump(nt, br.outputs['Fac'], 0.3, 0.002)
    b.invert = True
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_mirror(name='mirror'):
    return mat_plain(name, '#E9ECEC', rough=0.02, metal=1.0)


def mat_image(name, path, rough=0.7):
    m, nt, p = _mat(name)
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(path)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    L(nt, tc.outputs['UV'], tex.inputs['Vector'])
    L(nt, tex.outputs['Color'], p.inputs['Base Color'])
    inp(p, 'Roughness', rough)
    return m


def plane_uv(name, w, d, loc, mat=None, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = c
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    link(obj)
    if mat:
        me.materials.append(mat)
    return obj


def lamp_table(loc, base_mat, shade_mat, glow_mat, h=0.55):
    x, y, z = loc
    objs = [lathe('lamp_base', [(0, 0), (0.07, 0), (0.11, 0.08), (0.12, 0.18), (0.08, 0.3), (0.025, 0.34),
                                (0.02, h * 0.7), (0, h * 0.7)], (x, y, z), base_mat, 48)]
    shade = lathe('lamp_shade', [(0.17, 0), (0.14, 0.22)], (x, y, z + h * 0.62), shade_mat, 48)
    shade.modifiers.new('solid', 'SOLIDIFY').thickness = 0.004
    objs.append(shade)
    objs.append(sphere('lamp_bulb', 0.035, (x, y, z + h * 0.7), glow_mat))
    return objs


def towers(seed, x_range, y_range, count, base_z, mat_list, hmin=30, hmax=160, wmin=18, wmax=40):
    r = random.Random(seed)
    objs = []
    for i in range(count):
        w = r.uniform(wmin, wmax)
        d = r.uniform(wmin, wmax)
        h = r.uniform(hmin, hmax)
        x = r.uniform(*x_range)
        y = r.uniform(*y_range)
        objs.append(box(f'tower{i}', (w, d, h), (x, y, base_z + h / 2), r.choice(mat_list), smooth=False))
    return objs


def mat_oak_macro(name='oak_macro', light='#C99A64', dark='#7E5432'):
    """Close-up rift oak: fine straight grain lines + soft figure; grain runs along Y."""
    m, nt, p = _mat(name)
    v = coords(nt, (60, 1.2, 60))
    n1 = noise(nt, v, scale=1.0, detail=12, rough=0.66, distortion=0.4)
    r = ramp(nt, n1.outputs['Fac'], [(0.28, hex2lin(dark)), (0.52, hex2lin(light)), (0.8, hex2lin('#D6AE7C'))])
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_type = 'BANDS'
    w.bands_direction = 'X'
    inp(w, 'Scale', 26)
    inp(w, 'Distortion', 3.5)
    inp(w, 'Detail', 6)
    L(nt, coords(nt, (1, 0.12, 1)), w.inputs['Vector'])
    lines = ramp(nt, w.outputs['Fac'], [(0.0, (0.72, 0.72, 0.72, 1)), (0.18, (1, 1, 1, 1))])
    col = mix_rgb(nt, 0.75, r.outputs['Color'], lines.outputs['Color'], 'MULTIPLY')
    L(nt, col, p.inputs['Base Color'])
    inp(p, 'Roughness', 0.48)
    b = bump(nt, w.outputs['Fac'], 0.12, 0.001)
    L(nt, b.outputs['Normal'], p.inputs['Normal'])
    return m
