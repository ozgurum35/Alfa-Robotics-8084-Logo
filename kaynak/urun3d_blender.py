# Runs inside Blender (portable 5.2 + STEP Importer extension). Renders one FRC product from its official CAD
# with a transparent background (the 2D layout is composited later by urun3d.py).
# blender -b --python urun3d_blender.py -- <spec.json>
# spec: {"parts": [step paths] | "builtin": "battery", "rot": [x,y,z deg], "hide": [name substrings],
#        "az": deg, "el": deg, "lens": mm, "fill": 0..1, "w": px, "h": px, "samples": n,
#        "frames": [a, b] (turntable frames of 300) or null, "out": path (still .png or folder for frames)}
import bpy, sys, json, math, os, mathutils, addon_utils
from mathutils import Vector, Matrix

S = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
NF = 300
bpy.ops.wm.read_homefile(use_empty=True)
addon_utils.enable("bl_ext.user_default.step_importer", default_set=True)
sc = bpy.context.scene


def principled(m):
    if not m or not m.node_tree: return None
    return next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)

def new_mat(name, rgb, metal=0.0, rough=0.5, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = principled(m)
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    if coat: p.inputs["Coat Weight"].default_value = coat
    return m

def box(name, size, loc, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 4
    o.data.materials.append(mat); return o

def cyl(name, r, h, loc, mat, rot=(0, 0, 0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=verts); o = bpy.context.object
    o.name = name; o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o

def text_obj(body, size, loc, rot, mat, extrude=0.0005):
    bpy.ops.object.text_add(location=loc, rotation=rot); t = bpy.context.object; t.data.body = body; t.data.size = size
    t.data.align_x = "CENTER"; t.data.align_y = "CENTER"; t.data.extrude = extrude
    f = "C:/Windows/Fonts/bahnschrift.ttf"
    if os.path.exists(f): t.data.font = bpy.data.fonts.load(f, check_existing=True)
    t.data.materials.append(mat); return t


def build_battery():
    """MK ES17-12 sized SLA battery (181 x 76 x 167 mm) with 120 A breaker style leads - modelled, no official CAD."""
    blk = new_mat("case", (0.025, 0.025, 0.03), rough=0.55); lid = new_mat("lid", (0.04, 0.04, 0.045), rough=0.4)
    lab = new_mat("label", (0.22, 0.23, 0.25), rough=0.85); red = new_mat("red", (0.75, 0.03, 0.03), rough=0.35)
    cu = new_mat("tab", (0.8, 0.8, 0.82), metal=1.0, rough=0.25); ink = new_mat("ink", (0.02, 0.05, 0.12), rough=0.5)
    box("case", (0.181, 0.076, 0.155), (0, 0, 0.0775), blk, 0.004)
    box("lid", (0.183, 0.078, 0.014), (0, 0, 0.161), lid, 0.003)
    box("label", (0.150, 0.0008, 0.095), (0, -0.0382, 0.075), lab, 0.0)
    text_obj("12V  18Ah", 0.022, (0, -0.0392, 0.095), (math.pi / 2, 0, 0), ink)
    text_obj("SEALED LEAD ACID", 0.009, (0, -0.0392, 0.067), (math.pi / 2, 0, 0), ink)
    for x, m in ((-0.072, red), (0.072, blk)):
        box("tab", (0.0065, 0.016, 0.018), (x, 0, 0.176), cu)
        cyl("boot", 0.012, 0.03, (x, 0, 0.185), m)
    # leads to an SB50-style connector
    for k, (x, m) in enumerate(((-0.072, red), (0.072, blk))):
        pts = [(x, 0, 0.2), (x * 0.6, -0.02, 0.24), (0.0, -0.06, 0.25), (0.05 * (k * 2 - 1) * 0.2, -0.13, 0.215)]
        cu_ = bpy.data.curves.new("lead", "CURVE"); cu_.dimensions = "3D"; cu_.bevel_depth = 0.0055; sp = cu_.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
        o = bpy.data.objects.new("lead", cu_); sc.collection.objects.link(o); o.data.materials.append(m)
    box("sb50", (0.034, 0.04, 0.02), (0, -0.14, 0.212), new_mat("sb", (0.7, 0.04, 0.04), rough=0.4), 0.002)


PAL = {  # approximated finishes for CAD files that ship without colour (REV)
    "alu": ((0.62, 0.64, 0.67), 1.0, 0.3), "steel": ((0.55, 0.56, 0.58), 1.0, 0.22), "black": ((0.02, 0.02, 0.022), 0.0, 0.42),
    "anod": ((0.025, 0.025, 0.03), 0.7, 0.38), "dgrey": ((0.08, 0.085, 0.09), 0.0, 0.45), "white": ((0.8, 0.8, 0.8), 0.0, 0.4),
    "red": ((0.7, 0.02, 0.02), 0.0, 0.35), "orange": ((0.95, 0.32, 0.02), 0.0, 0.38), "copper": ((0.85, 0.45, 0.25), 1.0, 0.3),
    "green": ((0.05, 0.45, 0.12), 0.0, 0.4), "char": ((0.045, 0.048, 0.052), 0.0, 0.5), "blue": ((0.05, 0.25, 0.8), 0.0, 0.35)}
_pm = {}
# REV PDH (REV-11-1850): CAD has no colours; finishes from REV's product photo - charcoal housing, orange lever terminals,
# white label strips and print, green CAN connectors, metal contacts. Sizes in mm in the CAD frame.
PDH_PAINT = dict(mode="part", default="char", rules=[
    dict(mat="orange", size=s) for s in ((24, 28, 78), (28, 37, 32), (15, 11, 5), (12, 17, 30))] + [
    dict(mat="white", size=s) for s in ((26, 0, 9), (25, 0, 9), (10, 0, 5), (0, 5, 9))] + [
    dict(mat="green", size=s) for s in ((9, 17, 12), (7, 17, 12))] + [
    dict(mat="steel", size=s) for s in ((7, 11, 3), (19, 1, 5))] + [dict(mat="white", dmax=3), dict(mat="white", flat=True, dmax=12)])
def pal(k):
    if k not in _pm: c, m, r = PAL[k]; _pm[k] = new_mat("P_" + k, c, m, r)
    return _pm[k]

def rule_hit(r, c, dims=None):
    """c: centre in mm (CAD frame). Rule keys: box [x0,y0,z0,x1,y1,z1], rax axis + rmin/rmax (+ cx, cy), dmin/dmax (part size)."""
    if "box" in r:
        b = r["box"]
        if not all(b[i] <= c[i] <= b[i + 3] for i in range(3)): return False
    if "rax" in r:
        i = "xyz".index(r["rax"]); o = [j for j in range(3) if j != i]
        rr = math.hypot(c[o[0]] - r.get("cx", 0), c[o[1]] - r.get("cy", 0))
        if not r.get("rmin", 0) <= rr <= r.get("rmax", 1e9): return False
    if dims is not None and not r.get("dmin", 0) <= max(dims) <= r.get("dmax", 1e9): return False
    if r.get("flat") and (dims is None or dims[1] > 0.6): return False
    if "size" in r and (dims is None or any(abs(a - b) > 1.6 for a, b in zip(dims, r["size"]))): return False
    return True

def paint(objs, P):
    import bmesh
    if P["mode"] == "part":
        before = set(sc.objects)
        for o in list(objs):
            bpy.context.view_layer.objects.active = o; o.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT"); o.select_set(False)
        objs = list(objs) + [o for o in sc.objects if o not in before and o.type == "MESH"]
        for o in objs:
            pts = [o.matrix_world @ v.co for v in o.data.vertices]
            mn = [min(p[i] for p in pts) * 1000 for i in range(3)]; mx = [max(p[i] for p in pts) * 1000 for i in range(3)]
            c = [(a + b) / 2 for a, b in zip(mn, mx)]; d = [b - a for a, b in zip(mn, mx)]
            k = next((r["mat"] for r in P["rules"] if rule_hit(r, c, d)), P["default"])
            o.data.materials.clear(); o.data.materials.append(pal(k))
    else:
        for o in objs:
            keys = [P["default"]] + [r["mat"] for r in P["rules"]]; o.data.materials.clear()
            for k in dict.fromkeys(keys): o.data.materials.append(pal(k))
            names = list(dict.fromkeys(keys)); mw = o.matrix_world
            for poly in o.data.polygons:
                c = (mw @ poly.center) * 1000
                k = next((r["mat"] for r in P["rules"] if rule_hit(r, c)), P["default"]); poly.material_index = names.index(k)
    return objs


CADDIR = "D:/CLAUDE/Araclar/cad/"
MODS = []          # per swerve module: steer pivot, wheel spin empty, steer axis (robot frame), roll angle at steer 0
H = 0.343          # half of the 27 in frame
RW = 0.0508        # wheel radius (4 in wheel)


def grab(before):
    return [o for o in sc.objects if o not in before]

def adopt(objs, parent):
    bpy.context.view_layer.update()
    for o in objs:
        if o.parent is None or o.parent not in objs:
            mw = o.matrix_world.copy(); o.parent = parent; o.matrix_parent_inverse = parent.matrix_world.inverted(); o.matrix_world = mw

def place_cad(path, parent, loc, rot=(0, 0, 0), paint_=None):
    before = set(sc.objects); bpy.ops.import_scene.step(filepath=path); new = grab(before)
    E = bpy.data.objects.new("G", None); sc.collection.objects.link(E); adopt(new, E)
    bpy.context.view_layer.update()
    ms = [o for o in new if o.type == "MESH"]
    if paint_:
        for o in ms:
            bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
        ms = [o for o in grab(before) if o.type == "MESH"]
        for o in ms:
            vs = [o.matrix_world @ v.co for v in o.data.vertices]
            mn = [min(v[i] for v in vs) * 1000 for i in range(3)]; mx = [max(v[i] for v in vs) * 1000 for i in range(3)]
            c = [(a + b) / 2 for a, b in zip(mn, mx)]; d = [b - a for a, b in zip(mn, mx)]
            k = next((r["mat"] for r in paint_["rules"] if rule_hit(r, c, d)), paint_["default"])
            o.data.materials.clear(); o.data.materials.append(pal(k))
    E.rotation_euler = [math.radians(a) for a in rot]; bpy.context.view_layer.update()
    mn, mx = bounds(ms); E.location = Vector(loc) - Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    bpy.context.view_layer.update(); adopt([E], parent); return ms


def build_chassis():
    rob = bpy.data.objects.new("ROBOT", None); sc.collection.objects.link(rob)
    before = set(sc.objects); bpy.ops.import_scene.step(filepath=CADDIR + "mk4i_falcon.step"); first = grab(before)
    groups = [first]
    for _ in range(3):
        bpy.ops.object.select_all(action="DESELECT")
        for o in first: o.select_set(True)
        bpy.context.view_layer.objects.active = first[0]; bpy.ops.object.duplicate(linked=True)
        groups.append(list(bpy.context.selected_objects))
    Rx = Matrix.Rotation(math.pi / 2, 4, "X")                       # CAD is Y-up
    for k, g in enumerate(groups):
        sx, sy = [(1, -1), (1, 1), (-1, 1), (-1, -1)][k]
        M = bpy.data.objects.new(f"MOD{k}", None); sc.collection.objects.link(M); M.parent = rob
        M.location = (sx * H, sy * H, 0); M.rotation_euler.z = k * math.pi / 2; bpy.context.view_layer.update()
        root = next(o for o in g if o.parent is None or o.parent not in g)
        orig = root.matrix_world.copy(); root.parent = M; root.matrix_parent_inverse = Matrix.Identity(4); root.matrix_basis = Rx @ orig
        bpy.context.view_layer.update()
        find = lambda pre: next(o for o in g if o.name.startswith(pre))
        turret, wheel = find("MK4 Turret Assembly"), find("MK4 Billet Wheel Assembly")
        tread, bevel = find("Tread, Blue Nitrile"), find("Bevel Gear, 4515")
        wc = sum(bounds([tread]), Vector()) / 2; bc = sum(bounds([bevel]), Vector()) / 2
        ax = Vector((bc.x - wc.x, bc.y - wc.y, 0)).normalized(); roll = Vector((ax.y, -ax.x, 0))
        SP = bpy.data.objects.new(f"STEER{k}", None); sc.collection.objects.link(SP); SP.location = (wc.x, wc.y, 0)
        WA = bpy.data.objects.new(f"AXLE{k}", None); sc.collection.objects.link(WA); WA.location = wc
        WA.rotation_euler.z = math.atan2(ax.y, ax.x)
        WS = bpy.data.objects.new(f"SPIN{k}", None); sc.collection.objects.link(WS)
        bpy.context.view_layer.update(); adopt([SP], M); adopt([WA], SP)
        WS.parent = WA; bpy.context.view_layer.update()
        adopt([turret], SP); adopt([wheel], WS)
        MODS.append(dict(sp=SP, ws=WS, pos=Vector((wc.x, wc.y)), phi0=math.atan2(roll.y, roll.x)))
    # frame: 2x1 rails between the modules, belly pan
    alu = new_mat("P_rail", (0.42, 0.44, 0.47), 0.9, 0.5); pan = new_mat("P_pan", (0.03, 0.03, 0.035), 0.0, 0.5)
    # 2x1 tube on edge between the MK4i lower plate (44 mm) and middle plate (95 mm), through the module to the
    # frame corner; the module's 10-32 frame bolts sit 13 mm in from the edge = tube centre line
    zb_, th, tw = S.get("rail_bottom", 0.0445), 0.0508, 0.0254
    zc_ = zb_ + th / 2
    rails = [box("rail", (2 * H, tw, th), (0, s * (H - tw / 2), zc_), alu, 0.0015) for s in (-1, 1)]
    rails += [box("rail", (tw, 2 * H - 2 * tw - 0.001, th), (s * (H - tw / 2), 0, zc_), alu, 0.0015) for s in (-1, 1)]
    rails += [box("pan", (2 * H - 2 * tw, 2 * H - 0.38, 0.003), (0, 0, zb_ + 0.0015), pan, 0)]   # cross shaped, clear of the modules
    rails += [box("pan", (2 * H - 0.38, 2 * H - 2 * tw, 0.003), (0, 0, zb_ + 0.0014), pan, 0)]
    adopt(rails, rob)
    zp = zb_ + 0.003
    place_cad(CADDIR + "roborio2.step", rob, (0.075, 0.075, zp))
    place_cad(CADDIR + "pdh.step", rob, (0.0, -0.085, zp), rot=(90, 0, 0), paint_=PDH_PAINT)
    before = set(sc.objects); build_battery(); bat = grab(before)
    E = bpy.data.objects.new("BAT", None); sc.collection.objects.link(E); adopt(bat, E)
    E.rotation_euler.z = math.pi / 2; E.location = (-0.095, 0.075, zp); bpy.context.view_layer.update(); adopt([E], rob)
    # bumpers: blue fabric over 3/4 in plywood + pool noodles, team number on every side
    if not S.get("bumpers", True): return
    fab = new_mat("P_fabric", (0.012, 0.07, 0.42), 0.0, 0.85)
    pr = principled(bpy.data.materials["P_fabric"])
    if "Sheen Weight" in pr.inputs: pr.inputs["Sheen Weight"].default_value = 0.6
    wht = new_mat("P_num", (0.9, 0.9, 0.9), 0.0, 0.6)
    T, Hb, zb = 0.083, 0.127, 0.025; zc = zb + Hb / 2; bump = []
    bump.append(bumper_ring(H, H + T, zb, Hb, fab))
    for (x, y, rz) in ((0, -(H + T + 0.0012), 0), (H + T + 0.0012, 0, math.pi / 2), (0, H + T + 0.0012, math.pi), (-(H + T + 0.0012), 0, -math.pi / 2)):
        bump.append(text_obj("8084", 0.115, (x, y, zc), (math.pi / 2, 0, rz), wht, 0.0012))
    adopt(bump, rob)


def rrect(h, r, n=10):
    """square of half size h with corner radius r, counter-clockwise, 4 * (n + 1) points"""
    pts = []
    for q, (cx, cy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for i in range(n + 1):
            a = math.pi / 2 * (q + i / n); pts.append(((h - r) * cx + r * math.cos(a), (h - r) * cy + r * math.sin(a)))
    return pts

def bumper_ring(hi, ho, z0, hz, mat):
    import bmesh
    bm = bmesh.new(); I, O = rrect(hi, 0.004), rrect(ho, 0.07); n = len(I)
    v = [[bm.verts.new((x, y, z)) for x, y in L] for L, z in ((I, z0), (O, z0), (O, z0 + hz), (I, z0 + hz))]
    for k in range(4):
        A, B = v[k], v[(k + 1) % 4]
        for i in range(n): bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]))
    bm.normal_update(); me = bpy.data.meshes.new("bumper"); bm.to_mesh(me)
    o = bpy.data.objects.new("bumper", me); sc.collection.objects.link(o); me.materials.append(mat)
    for poly in me.polygons: poly.use_smooth = True
    b = o.modifiers.new("b", "BEVEL"); b.width = 0.03; b.segments = 8; b.limit_method = "ANGLE"; b.angle_limit = math.radians(50)
    if hasattr(b, "harden_normals"): b.harden_normals = False
    return o


def drive_pose(t, centred=False):
    """robot follows a circle while its heading swings; every module steers and spins from swerve kinematics"""
    Rc, tha, n = S.get("path_r", 0.28), S.get("tha", 0.45), 600
    rob = bpy.data.objects["ROBOT"]
    if "base" not in rob: rob["base"] = list(rob.location)
    b = Vector(rob["base"])
    def state(u):
        a = 2 * math.pi * u; th = tha * math.sin(a + 0.7)
        v = Vector((-math.sin(a), math.cos(a))) * Rc * 2 * math.pi; w = tha * math.cos(a + 0.7) * 2 * math.pi
        vr = Vector((v.x * math.cos(-th) - v.y * math.sin(-th), v.x * math.sin(-th) + v.y * math.cos(-th)))
        return a, th, [vr + Vector((-w * m["pos"].y, w * m["pos"].x)) for m in MODS]
    if not hasattr(drive_pose, "tab"):          # integrate steer (unwrapped) and wheel spin over one loop
        ang = [None] * 4; spin = [0.0] * 4; tab = []
        for i in range(n + 1):
            _, _, vs = state(i / n); row = []
            for k, v in enumerate(vs):
                a = math.atan2(v.y, v.x)
                if ang[k] is not None: a = ang[k] + (a - ang[k] + math.pi) % (2 * math.pi) - math.pi
                ang[k] = a
                if i: spin[k] += v.length / n / RW
                row.append((a, spin[k]))
            tab.append(row)
        sc_ = [max(1, round(s / (2 * math.pi))) * 2 * math.pi / s for s in spin]     # whole turns -> seamless loop
        drive_pose.tab = [[(a, s * sc_[k]) for k, (a, s) in enumerate(r)] for r in tab]
    a, th, _ = state(t); row = drive_pose.tab[round(t * n) % n]
    rob.location = b if centred else b + Vector((Rc * math.cos(a), Rc * math.sin(a), 0))
    rob.rotation_euler.z = th
    for m, (st, sp) in zip(MODS, row):
        m["sp"].rotation_euler.z = st - m["phi0"]; m["ws"].rotation_euler.x = sp


def import_parts():
    if S.get("builtin") == "battery": build_battery()
    if S.get("builtin") == "chassis": build_chassis()
    offs = S.get("offsets", [])
    for i, p in enumerate(S.get("parts", [])):
        before = set(sc.objects); bpy.ops.import_scene.step(filepath=p)
        if i < len(offs):
            for o in set(sc.objects) - before:
                if o.parent is None: o.location += Vector(offs[i][:3]) / 1000
                if o.parent is None and len(offs[i]) > 3: o.rotation_euler.rotate(mathutils.Euler([math.radians(a) for a in offs[i][3:6]]))
    bpy.context.view_layer.update()
    objs = [o for o in sc.objects if o.type in ("MESH", "CURVE", "FONT")]
    if S.get("paint") == "PDH": S["paint"] = PDH_PAINT
    if S.get("paint"): objs = paint([o for o in objs if o.type == "MESH"], S["paint"]) + [o for o in objs if o.type != "MESH"]
    for o in objs:
        if any(h.lower() in o.name.lower() for h in S.get("hide", [])): o.hide_render = True
    return [o for o in objs if not o.hide_render]


def tune_materials(objs):
    done = set()
    for o in objs:
        for m in o.data.materials:
            p = principled(m)
            if not p or m.name in done or m.name.startswith("P_"): continue
            done.add(m.name)
            c = p.inputs["Base Color"].default_value; r, g, b = c[:3]; mx_, mn_ = max(r, g, b), min(r, g, b)
            if mx_ - mn_ < 0.06 and mx_ > 0.35 and p.inputs["Metallic"].default_value < 0.5:   # light grey -> machined aluminium
                p.inputs["Metallic"].default_value = 0.9; p.inputs["Roughness"].default_value = 0.32
            elif mx_ < 0.12:                                                                       # black plastic / anodised
                p.inputs["Roughness"].default_value = max(0.35, min(0.55, p.inputs["Roughness"].default_value))
            else:
                p.inputs["Roughness"].default_value = min(0.5, p.inputs["Roughness"].default_value)
    for o in objs:
        if o.type == "MESH":
            for poly in o.data.polygons: poly.use_smooth = True
            if hasattr(o.data, "set_sharpen_by_angle"): pass


def bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get(); mn = Vector((1e9,) * 3); mx = -mn
    for o in objs:
        for c in o.evaluated_get(dg).bound_box:
            v = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, v)); mx = Vector(map(max, mx, v))
    return mn, mx


if __name__ == "__main__":
    objs = import_parts()
    tune_materials(objs)
    if MODS: drive_pose(S.get("pose", 0.1), centred=True)
    # orient: rotate everything about the origin, then put it on the floor, centred
    R = mathutils.Euler([math.radians(a) for a in S.get("rot", (0, 0, 0))], S.get("order", "XYZ")).to_matrix().to_4x4()
    roots = [o for o in sc.objects if o.parent is None]
    for o in roots: o.matrix_world = R @ o.matrix_world
    bpy.context.view_layer.update()
    mn, mx = bounds(objs)
    T = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
    pivot = bpy.data.objects.new("PIVOT", None); sc.collection.objects.link(pivot)
    for o in roots: o.matrix_world = T @ o.matrix_world; o.parent = pivot; o.matrix_parent_inverse = pivot.matrix_world.inverted()
    bpy.context.view_layer.update()
    mn, mx = bounds(objs); dim = mx - mn
    rad = max(math.hypot(dim.x, dim.y) / 2, dim.z / 2) * 1.02          # radius of the turntable footprint / height

    # floor (shadow catcher), world, lights
    bpy.ops.mesh.primitive_plane_add(size=max(dim) * 30, location=(0, 0, 0)); fl = bpy.context.object; fl.is_shadow_catcher = True
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.06, 0.12, 1); bg.inputs[1].default_value = 0.35
    size = max(dim.length, 0.05)
    def area(name, loc, energy, color, sz):
        L = bpy.data.lights.new(name, "AREA"); L.energy = energy * size ** 2; L.color = color; L.size = sz * size; L.shape = "DISK"
        o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = Vector(loc) * size
        o.rotation_euler = (Vector((0, 0, dim.z * 0.4)) - o.location).to_track_quat("-Z", "Y").to_euler()
    area("key", (-1.2, -1.6, 1.8), 26, (1.0, 0.97, 0.93), 1.2)
    area("fill", (1.8, -1.0, 0.7), 7, (0.85, 0.9, 1.0), 1.5)
    area("rimL", (-1.6, 1.6, 1.0), 30, (0.25, 0.6, 1.0), 0.8)
    area("rimR", (1.6, 1.4, 1.3), 26, (0.35, 0.75, 1.0), 0.8)
    area("top", (0, 0.2, 2.6), 8, (1, 1, 1), 2.0)

    # camera: fit the bounding sphere of the turning product into the frame
    W_, H_ = S["w"], S["h"]; sc.render.resolution_x, sc.render.resolution_y = W_, H_
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = S.get("lens", 80); cam.data.sensor_fit = "AUTO"
    el, az = math.radians(S.get("el", 18)), math.radians(S.get("az", -35))
    target = Vector((0, 0, dim.z * 0.5)); rs = math.sqrt((max(dim.x, dim.y) / 2) ** 2 * 2 + (dim.z / 2) ** 2) if S.get("frames") else 0
    if MODS and S.get("frames"): rs = math.hypot(dim.x, dim.y) / 2 + S.get("path_r", 0.28)
    cam.rotation_euler = (math.pi / 2 - el, 0, az)
    fov = 2 * math.atan(36 / 2 / cam.data.lens)                        # horizontal fov of the 36 mm sensor (fit = AUTO -> larger side)
    fov_s = fov if W_ >= H_ else 2 * math.atan(math.tan(fov / 2) * W_ / H_)   # fov along the smaller side
    def place(d): cam.location = target + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * d
    fill = S.get("fill", 0.82)
    if S.get("frames"):
        d = rs / math.sin(fov_s / 2 * fill); place(d)
    else:   # still: fit the actual projected bounding box
        bpy.context.view_layer.update(); d = size * 2; place(d)
        from bpy_extras.object_utils import world_to_camera_view
        for _ in range(4):
            bpy.context.view_layer.update()
            corners = [Vector((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
            pr = [world_to_camera_view(sc, cam, c) for c in corners]
            ext = max(max(abs(p.x - 0.5) * 2 for p in pr), max(abs(p.y - 0.5) * 2 for p in pr))
            cy = (min(p.y for p in pr) + max(p.y for p in pr)) / 2
            target.z += (cy - 0.5) * (d * math.tan(fov_s / 2)) * 0.8
            d *= ext / fill; place(d)

    # render settings
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.samples = S.get("samples", 128)
    sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"; sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
    sc.cycles.max_bounces = 6

    if S.get("frames"):
        a, b = S["frames"]; os.makedirs(S["out"], exist_ok=True); base = pivot.rotation_euler.z
        for i in range(a, b):
            if MODS: drive_pose(i / NF)
            else: pivot.rotation_euler.z = base + 2 * math.pi * i / NF
            sc.render.filepath = os.path.join(S["out"], f"{i:03d}.png"); bpy.ops.render.render(write_still=True)
    else:
        sc.render.filepath = S["out"]; bpy.ops.render.render(write_still=True)
    print("DONE", S["out"])
