import os, json, bpy

EXPORT_DIR = os.path.abspath("exports")
MODEL_DIR  = os.path.join(EXPORT_DIR, "models")
TEX_DIR    = os.path.join(EXPORT_DIR, "textures")
ANIM_DIR   = os.path.join(EXPORT_DIR, "animations")
CHAR_DIR   = os.path.join(MODEL_DIR, "characters")
SODA_FILE  = os.path.join(EXPORT_DIR, "recorded_data.soda")

# 1) Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2) Load textures
for fn in os.listdir(TEX_DIR):
    if fn.lower().endswith(".png"):
        img = bpy.data.images.load(os.path.join(TEX_DIR,fn))
        mat = bpy.data.materials.new(fn)
        tex = bpy.data.textures.new(fn, type='IMAGE')
        tex.image = img

# 3) Import global models/primitives
models = {}
for fn in os.listdir(MODEL_DIR):
    path = os.path.join(MODEL_DIR,fn); name,ext = os.path.splitext(fn)
    if ext.lower()==".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
        models[name] = bpy.context.selected_objects[:]
    elif ext.lower()==".json":
        desc = json.load(open(path))
        if desc['primitive']=="Part":
            bpy.ops.mesh.primitive_cube_add(size=1)
        else:
            bpy.ops.mesh.primitive_cone_add(vertices=4)
        o = bpy.context.object
        sx,sy,sz = desc['size']; o.scale=(sx/2,sy/2,sz/2)
        models[name] = [o]

# 4) Import animations
for fn in os.listdir(ANIM_DIR):
    if fn.lower().endswith(".rbxanim"):
        bpy.ops.import_scene.rbxanim(filepath=os.path.join(ANIM_DIR,fn))

# 5) Import characters
for cname in os.listdir(CHAR_DIR):
    parts = []
    cpath = os.path.join(CHAR_DIR,cname)
    for fn in os.listdir(cpath):
        p = os.path.join(cpath,fn); _,ext=os.path.splitext(fn)
        if ext.lower()==".fbx":
            bpy.ops.import_scene.fbx(filepath=p)
            parts += bpy.context.selected_objects[:]
        elif ext.lower()==".json":
            desc = json.load(open(p))
            if desc['primitive']=="Part":
                bpy.ops.mesh.primitive_cube_add(size=1)
            else:
                bpy.ops.mesh.primitive_cone_add(vertices=4)
            o = bpy.context.object
            sx,sy,sz=desc['size']; o.scale=(sx/2,sy/2,sz/2)
            parts.append(o)
    # group under empty
    empty = bpy.data.objects.new(cname, None)
    bpy.context.collection.objects.link(empty)
    for o in parts: o.parent = empty

# 6) Load replay data
soda = json.load(open(SODA_FILE))

# 7) Position map parts
for part in soda['map']:
    key = f"mesh_{''.join(filter(str.isdigit, str(part.get('meshId',''))))}"
    if key in models:
        for o in models[key]:
            o.location = part['pos']
            o.rotation_euler = [r*3.14159/180 for r in part['rot']]

# 8) Animate players (empties)
players = {}
for idx,p in enumerate(soda['frames'][0]['players']):
    emp = bpy.data.objects.new(f"Player_{p['name']}", None)
    bpy.context.collection.objects.link(emp)
    players[idx] = emp

for f,frame in enumerate(soda['frames'], start=1):
    bpy.context.scene.frame_set(f)
    for idx,p in enumerate(frame['players']):
        obj = players[idx]
        obj.location = p['pos']
        obj.rotation_euler = [math.radians(r) for r in p['rot']]
        obj.keyframe_insert("location", frame=f)
        obj.keyframe_insert("rotation_euler", frame=f)

bpy.context.scene.frame_end = len(soda['frames'])
print("✅ Import & animation done")