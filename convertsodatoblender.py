# File: import_soda_to_blender.py

import os, json, bpy, math

EXPORT_DIR = os.path.abspath("exports")
MODEL_DIR  = os.path.join(EXPORT_DIR, "models")
TEX_DIR    = os.path.join(EXPORT_DIR, "textures")
ANIM_DIR   = os.path.join(EXPORT_DIR, "animations")
CHAR_DIR   = os.path.join(MODEL_DIR, "characters")
GUI_DIR    = os.path.join(EXPORT_DIR, "gui")
SND_DIR    = os.path.join(EXPORT_DIR, "sounds")
SODA_FILE  = os.path.join(EXPORT_DIR, "recorded_data.soda")

# 1) Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2) Load textures
for fn in os.listdir(TEX_DIR):
    if fn.lower().endswith(".png"):
        img = bpy.data.images.load(os.path.join(TEX_DIR, fn))
        mat = bpy.data.materials.new(name=fn)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        texNode = mat.node_tree.nodes.new("ShaderNodeTexImage")
        texNode.image = img
        mat.node_tree.links.new(bsdf.inputs['Base Color'], texNode.outputs['Color'])

# 3) Import models & primitives
models = {}
for fn in os.listdir(MODEL_DIR):
    path = os.path.join(MODEL_DIR, fn)
    name, ext = os.path.splitext(fn)
    if ext.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
        models[name] = bpy.context.selected_objects[:]
    elif ext.lower() == ".json":
        desc = json.load(open(path))
        if desc['primitive'] == "Part":
            bpy.ops.mesh.primitive_cube_add(size=1)
        else:
            bpy.ops.mesh.primitive_cone_add(vertices=4)
        o = bpy.context.object
        sx, sy, sz = desc['size']
        o.scale = (sx/2, sy/2, sz/2)
        models[name] = [o]

# 4) Import animations (.rbxanim)
for fn in os.listdir(ANIM_DIR):
    if fn.lower().endswith(".rbxanim"):
        bpy.ops.import_scene.rbxanim(filepath=os.path.join(ANIM_DIR, fn))

# 5) Import characters
for cname in os.listdir(CHAR_DIR):
    parts = []
    cpath = os.path.join(CHAR_DIR, cname)
    for fn in os.listdir(cpath):
        ppath = os.path.join(cpath, fn)
        _, ext = os.path.splitext(fn)
        if ext.lower() == ".fbx":
            bpy.ops.import_scene.fbx(filepath=ppath)
            parts += bpy.context.selected_objects[:]
        elif ext.lower() == ".json":
            desc = json.load(open(ppath))
            if desc['primitive'] == "Part":
                bpy.ops.mesh.primitive_cube_add(size=1)
            else:
                bpy.ops.mesh.primitive_cone_add(vertices=4)
            o = bpy.context.object
            sx, sy, sz = desc['size']
            o.scale = (sx/2, sy/2, sz/2)
            parts.append(o)
    empty = bpy.data.objects.new(cname, None)
    bpy.context.collection.objects.link(empty)
    for o in parts:
        o.parent = empty

# 6) Load replay data
soda = json.load(open(SODA_FILE))

# 7) Position map parts
for part in soda['map']:
    key = f"mesh_{''.join(filter(str.isdigit, str(part.get('meshId',''))))}"
    if key in models:
        for o in models[key]:
            o.location = part['pos']
            o.rotation_euler = [math.radians(r) for r in part['rot']]

# 8) Animate players (empty rigs)
players = {}
for i, p in enumerate(soda['frames'][0]['players']):
    emp = bpy.data.objects.new(f"Player_{p['name']}", None)
    bpy.context.collection.objects.link(emp)
    players[i] = emp

for f_idx, frame in enumerate(soda['frames'], start=1):
    bpy.context.scene.frame_set(f_idx)
    for i, p in enumerate(frame['players']):
        obj = players[i]
        obj.location = p['pos']
        obj.rotation_euler = [math.radians(r) for r in p['rot']]
        obj.keyframe_insert(data_path="location", frame=f_idx)
        obj.keyframe_insert(data_path="rotation_euler", frame=f_idx)

# 9) Animate GUI text
text_objs = {}
for f_idx, frame in enumerate(soda['frames'], start=1):
    bpy.context.scene.frame_set(f_idx)
    for item in frame.get('guiState', []):
        path, txt, vis = item['path'], item['text'], item['visible']
        name = f"GUI_{path.replace('.', '_')}"
        if name not in text_objs:
            bpy.ops.object.text_add(location=(0, 0, 0))
            tobj = bpy.context.object
            tobj.name = name
            text_objs[name] = tobj
        else:
            tobj = text_objs[name]
        tobj.data.body = txt
        tobj.hide_viewport = not vis
        tobj.data.keyframe_insert("body", frame=f_idx)
        tobj.keyframe_insert("hide_viewport", frame=f_idx)

# 10) Import GUI images as planes
for fn in os.listdir(GUI_DIR):
    path = os.path.join(GUI_DIR, fn)
    img = bpy.data.images.load(path)
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.object
    mat = bpy.data.materials.new(name=fn)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texNode = mat.node_tree.nodes.new("ShaderNodeTexImage")
    texNode.image = img
    mat.node_tree.links.new(bsdf.inputs["Base Color"], texNode.outputs["Color"])
    plane.data.materials.append(mat)
    plane.location = (0, 0, 0)

# 11) Import sounds as speakers
for fn in os.listdir(SND_DIR):
    path = os.path.join(SND_DIR, fn)
    snd = bpy.data.sounds.load(path)
    spk = bpy.data.objects.new(fn, bpy.data.speakers.new(fn))
    spk.data.sound = snd
    bpy.context.collection.objects.link(spk)
    spk.location = (0, 0, 0)

# 12) Save .blend
bpy.context.scene.frame_end = len(soda['frames'])
blend_out = os.path.join(EXPORT_DIR, "replay.blend")
bpy.ops.wm.save_mainfile(filepath=blend_out)
print("✅ Saved .blend →", blend_out)