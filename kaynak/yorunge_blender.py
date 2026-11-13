# Runs inside Blender: FRC parts (or the swerve robot) orbit the ALFA logo on a tilted ring.
# The logo is a holdout plane (its alpha cuts whatever passes behind it); the 2D neon logo is composited later
# by yorunge.py at the projected rectangle written to <out>.json.
# blender -b --python yorunge_blender.py -- <spec.json>
import bpy, sys, os, json, math
from mathutils import Vector, Euler, Matrix, Quaternion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urun3d_blender as U          # loads the same spec, resets the scene, enables the STEP importer
from bpy_extras.object_utils import world_to_camera_view

S, sc = U.S, U.sc
NF = 300
CAD = U.CADDIR


def load_part(ps):
    before = set(sc.objects)
    if ps.get("builtin") == "battery": U.build_battery()
    offs = ps.get("offsets", [])
    for i, p in enumerate(ps.get("parts", [])):
        b2 = set(sc.objects); bpy.ops.import_scene.step(filepath=CAD + p)
        if i < len(offs):
            for o in set(sc.objects) - b2:
                if o.parent is None:
                    o.location += Vector(offs[i][:3]) / 1000
                    if len(offs[i]) > 3: o.rotation_euler.rotate(Euler([math.radians(a) for a in offs[i][3:6]]))
    bpy.context.view_layer.update()
    vis = [o for o in U.grab(before) if o.type in ("MESH", "CURVE", "FONT")]
    for o in vis:
        if any(h.lower() in o.name.lower() for h in ps.get("hide", [])): o.hide_render = True
    vis = [o for o in vis if not o.hide_render]
    P = U.PDH_PAINT if ps.get("paint") == "PDH" else ps.get("paint")
    if P: U.paint([o for o in vis if o.type == "MESH"], P)
    vis = [o for o in U.grab(before) if o.type in ("MESH", "CURVE", "FONT") and not o.hide_render]
    U.tune_materials(vis)
    new = U.grab(before); G = bpy.data.objects.new("G", None); sc.collection.objects.link(G); U.adopt(new, G)
    G.rotation_euler = Euler([math.radians(a) for a in ps.get("rot", (0, 0, 0))], ps.get("order", "XYZ"))
    bpy.context.view_layer.update()
    mn, mx = U.bounds(vis); c = (mn + mx) / 2; G.location -= c
    K = bpy.data.objects.new("K", None); sc.collection.objects.link(K); bpy.context.view_layer.update(); U.adopt([G], K)
    K.scale = [S["size"] / max(mx - mn)] * 3
    K.rotation_mode = "ZXY"          # spin about its own vertical first, then lean toward the camera
    ps["_vis"] = vis
    return K, ps


def logo_plane():
    img = bpy.data.images.load(S["logo"]); asp = img.size[0] / img.size[1]; h = S["logo_h"]
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, S.get("logo_z", 0))); pl = bpy.context.object
    pl.scale = (h * asp, h, 1); pl.rotation_euler = (math.pi / 2 - math.radians(S.get("el", 12)), 0, 0)
    m = bpy.data.materials.new("logo_holdout"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    hold = nt.nodes.new("ShaderNodeHoldout"); tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Alpha"], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(hold.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0]); pl.data.materials.append(m)
    pl.visible_shadow = False
    return pl


# ---------------------------------------------------------------- scene
pl = logo_plane()
ring = Euler([math.radians(a) for a in S["ring"]], "XYZ").to_matrix()
R = S["R"]
items = []
if S["kind"] == "robot":
    U.build_chassis(); rob = bpy.data.objects["ROBOT"]; k_ = S.get("rob_scale", 1.0); rob.scale = (k_, k_, k_); U.RW *= k_     # bigger robot, wheel spin kept true to its size
    rob.location = (0, 0, S.get("floor", -0.6) + 0.019 * k_)
    vis = [o for o in sc.objects if o.type in ("MESH", "CURVE", "FONT") and o != pl]
    U.tune_materials(vis)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, S.get("floor", -0.6))); bpy.context.object.is_shadow_catcher = True
else:
    for ps in S["items"]: items.append(load_part(ps))

LZ, LS = pl.location.z, pl.scale.copy()
def pose(t):
    # the logo floats, breathes and rocks gently (whole cycles per loop, so the loop stays seamless)
    la = S.get("logo_anim", dict(bob=0.035, breath=0.03, rock=3.0))
    pl.location.z = LZ + la["bob"] * S["logo_h"] * math.sin(2 * math.pi * t)
    pl.scale = LS * (1 + la["breath"] * math.sin(4 * math.pi * t))
    pl.rotation_euler = (math.pi / 2 - math.radians(S.get("el", 12)), math.radians(la["rock"]) * math.sin(2 * math.pi * t + 1.2), 0)
    if S["kind"] == "robot":
        U.drive_pose(t)
        if S.get("ride"):           # the logo rides above the robot, so the robot is never hidden behind it
            rb = bpy.data.objects["ROBOT"].location
            pl.location.x, pl.location.y = rb.x, rb.y
            pl.location.z = S["floor"] + S["ride"] + S["logo_h"] / 2 + la["bob"] * S["logo_h"] * math.sin(2 * math.pi * t)
        return
    n = len(items)
    bpy.context.view_layer.update()
    for k, (K, ps) in enumerate(items):
        a = 2 * math.pi * (k / n + t)
        K.location = ring @ Vector((R * math.cos(a), R * math.sin(a), 0)); K.location.z *= S.get("stretch", 1.0)
        # the side shown in the product's own render (its logo / print) always turns toward the camera; gentle sway only
        az, el = math.radians(ps.get("az", -35)), math.radians(ps.get("el", 14))
        dp = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
        dc = (cam.location - K.location).normalized()
        q = dc.to_track_quat("-Y", "Z") @ dp.to_track_quat("-Y", "Z").inverted()
        sw = math.radians(10) * math.sin(2 * math.pi * t + k * 2.1)
        K.rotation_mode = "QUATERNION"; K.rotation_quaternion = Quaternion((0, 0, 1), sw) @ q
    bpy.context.view_layer.update()

def logo_rect():
    """projected logo: centre, width (render px) and screen angle (deg, counter-clockwise)"""
    bpy.context.view_layer.update()
    c = [world_to_camera_view(sc, cam, pl.matrix_world @ Vector(v)) for v in ((-0.5, 0.5, 0), (0.5, 0.5, 0), (0, 0, 0))]
    dx, dy = (c[1].x - c[0].x) * S["w"], (c[1].y - c[0].y) * S["h"]
    return dict(cx=c[2].x * S["w"], cy=(1 - c[2].y) * S["h"], lw=math.hypot(dx, dy), ang=math.degrees(math.atan2(dy, dx)))

# lights (scaled to the scene)
size = 2 * R + S["logo_h"]
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.06, 0.12, 1); bg.inputs[1].default_value = 0.35
def area(name, loc, e, col, sz):
    L = bpy.data.lights.new(name, "AREA"); L.energy = e * size ** 2; L.color = col; L.size = sz * size; L.shape = "DISK"
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = Vector(loc) * size
    o.rotation_euler = (-o.location).to_track_quat("-Z", "Y").to_euler()
area("key", (-1.0, -1.6, 1.4), 34, (1.0, 0.97, 0.93), 1.0)
area("fill", (1.6, -1.2, 0.3), 8, (0.85, 0.9, 1.0), 1.2)
area("rimL", (-1.5, 1.4, 0.8), 30, (0.25, 0.6, 1.0), 0.8)
area("rimR", (1.5, 1.4, 1.0), 26, (0.35, 0.75, 1.0), 0.8)
area("core", (0, 0.15, 0), 3, (0.3, 0.65, 1.0), 0.35)        # blue light from the logo itself

# camera fitted to everything the loop ever shows
W_, H_ = S["w"], S["h"]; sc.render.resolution_x, sc.render.resolution_y = W_, H_
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = S.get("lens", 50)
el = math.radians(S.get("el", 12)); tgt = Vector((0, 0, S.get("tz", 0)))
def place(d):
    cam.location = tgt + Vector((0, -math.cos(el), math.sin(el))) * d
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
pts = L4 = [pl.matrix_world @ Vector((x, y, 0)) for x in (-0.5, 0.5) for y in (-0.5, 0.5)]
if S["kind"] == "robot":
    hb = (0.343 + 0.083) * S.get("rob_scale", 1.0); fz = S.get("floor", -0.6)
    if S.get("ride"):
        hw = S["logo_h"] * pl.scale.x / pl.scale.y / 2; zc = fz + S["ride"] + S["logo_h"] / 2
        pts = [Vector((S["path_r"] * math.cos(a) + dx, S["path_r"] * math.sin(a), zc + dz)) for a in [i * math.pi / 12 for i in range(24)]
               for dx in (-hw, hw) for dz in (-S["logo_h"] / 2, S["logo_h"] / 2)]
    pts += [Vector((S["path_r"] * math.cos(a) + dx, S["path_r"] * math.sin(a) + dy, fz + dz))
            for a in [i * math.pi / 12 for i in range(24)] for dx in (-hb, hb) for dy in (-hb, hb) for dz in (0, 0.2 * S.get("rob_scale", 1.0))]
else:
    rr = S["size"] * 0.6
    def on_ring(a): v = ring @ Vector((R * math.cos(a), R * math.sin(a), 0)); v.z *= S.get("stretch", 1.0); return v
    pts += [on_ring(a) + Vector(o) * rr
            for a in [i * math.pi / 12 for i in range(24)] for o in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
d = size * 2; place(d); fill = S.get("fill", 0.9)
for _ in range(6):
    bpy.context.view_layer.update()
    pr = [world_to_camera_view(sc, cam, p) for p in pts]
    ex = max(max(abs(p.x - 0.5) for p in pr) * 2, max(abs(p.y - 0.5) for p in pr) * 2)
    cy = (min(p.y for p in pr) + max(p.y for p in pr)) / 2
    tgt.z += (cy - 0.5) * 2 * d * math.tan(cam.data.angle / 2) * (H_ / max(W_, H_)) * 0.9
    d *= ex / fill; place(d)
bpy.context.view_layer.update()
lp = [world_to_camera_view(sc, cam, p) for p in L4]
json.dump(dict(x0=min(p.x for p in lp) * W_, x1=max(p.x for p in lp) * W_, y0=(1 - max(p.y for p in lp)) * H_, y1=(1 - min(p.y for p in lp)) * H_),
          open(S["out"].rstrip("/\\") + ".json", "w"))

cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
for dv in cp.devices: dv.use = dv.type == "OPTIX"
sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.samples = S.get("samples", 96)
sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"; sc.render.film_transparent = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"; sc.cycles.max_bounces = 6

if S.get("frames"):
    a, b = S["frames"]; os.makedirs(S["out"], exist_ok=True)
    for i in range(a, b):
        pose(i / NF); sc.render.filepath = os.path.join(S["out"], f"{i:03d}.png"); bpy.ops.render.render(write_still=True)
        json.dump(logo_rect(), open(os.path.join(S["out"], f"{i:03d}.json"), "w"))
else:
    pose(S.get("pose", 0.04)); sc.render.filepath = S["out"]; bpy.ops.render.render(write_still=True)
    json.dump(logo_rect(), open(S["out"] + ".logo.json", "w"))
print("DONE", S["out"])
