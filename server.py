# File: asset_server.py

from flask import Flask, request, jsonify
import os, json, requests

app = Flask(__name__)
EXPORT_DIR = "exports"
MODEL_DIR  = os.path.join(EXPORT_DIR, "models")
TEX_DIR    = os.path.join(EXPORT_DIR, "textures")
ANIM_DIR   = os.path.join(EXPORT_DIR, "animations")
CHAR_DIR   = os.path.join(MODEL_DIR, "characters")
GUI_DIR    = os.path.join(EXPORT_DIR, "gui")
SND_DIR    = os.path.join(EXPORT_DIR, "sounds")

for d in (EXPORT_DIR, MODEL_DIR, TEX_DIR, ANIM_DIR, CHAR_DIR, GUI_DIR, SND_DIR):
    os.makedirs(d, exist_ok=True)

def download_asset(aid, dest):
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={aid}"
    print(f"→ Downloading {aid} → {dest}…", end="")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)
    print(" done.")

@app.route("/record", methods=["POST"])
def record_data():
    data = request.get_json()
    path = os.path.join(EXPORT_DIR, "recorded_data.soda")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved replay → {path}")
    return jsonify(status="ok"), 200

@app.route("/assets", methods=["POST"])
def receive_assets():
    d = request.get_json()
    print(f"🔄 /assets: models={len(d['models'])}, textures={len(d['textures'])}, "
          f"anims={len(d['animations'])}, chars={len(d['characters'])}, "
          f"gui={len(d['guiImages'])}, sounds={len(d['sounds'])}")

    # Meshes & primitives
    for m in d["models"]:
        if isinstance(m, str):
            aid = "".join(filter(str.isdigit, m))
            dst = os.path.join(MODEL_DIR, f"mesh_{aid}.fbx")
            if not os.path.exists(dst):
                try:
                    download_asset(aid, dst)
                except Exception as e:
                    print("✖️ mesh", aid, e)
            else:
                print(f"• mesh_{aid}.fbx exists")
        else:
            name = f"prim_{m['primitive']}_{m['size'][0]}x{m['size'][1]}x{m['size'][2]}.json"
            with open(os.path.join(MODEL_DIR, name), "w") as f:
                json.dump(m, f)
            print(f"✔️ Wrote {name}")

    # Textures
    for t in d["textures"]:
        aid, dst = "".join(filter(str.isdigit, t)), os.path.join(TEX_DIR, f"tex_{aid}.png")
        if not os.path.exists(dst):
            try:
                download_asset(aid, dst)
            except Exception as e:
                print("✖️ tex", aid, e)
        else:
            print(f"• tex_{aid}.png exists")

    # Animations
    for a in d["animations"]:
        aid, dst = "".join(filter(str.isdigit, a)), os.path.join(ANIM_DIR, f"anim_{aid}.rbxanim")
        if not os.path.exists(dst):
            try:
                download_asset(aid, dst)
            except Exception as e:
                print("✖️ anim", aid, e)
        else:
            print(f"• anim_{aid}.rbxanim exists")

    # Characters
    for char in d["characters"]:
        cdir = os.path.join(CHAR_DIR, char["name"])
        os.makedirs(cdir, exist_ok=True)
        print(f"— char {char['name']}")
        for p in char["parts"]:
            if "meshId" in p:
                aid, dst = "".join(filter(str.isdigit, p["meshId"])), os.path.join(cdir, f"mesh_{aid}.fbx")
                if not os.path.exists(dst):
                    try:
                        download_asset(aid, dst)
                    except Exception as e:
                        print("✖️ char mesh", aid, e)
                else:
                    print(f"• char mesh_{aid}.fbx exists")
            else:
                name = f"prim_{p['primitive']}_{p['size'][0]}x{p['size'][1]}x{p['size'][2]}.json"
                with open(os.path.join(cdir, name), "w") as f:
                    json.dump(p, f)
                print(f"✔️ Wrote char {name}")

    # GUI images
    for g in d["guiImages"]:
        aid, dst = "".join(filter(str.isdigit, g)), os.path.join(GUI_DIR, f"gui_{aid}.png")
        if not os.path.exists(dst):
            try:
                download_asset(aid, dst)
            except Exception as e:
                print("✖️ gui", aid, e)
        else:
            print(f"• gui_{aid}.png exists")

    # Sounds
    for s in d["sounds"]:
        aid, dst = "".join(filter(str.isdigit, s)), os.path.join(SND_DIR, f"sound_{aid}.ogg")
        if not os.path.exists(dst):
            try:
                download_asset(aid, dst)
            except Exception as e:
                print("✖️ sound", aid, e)
        else:
            print(f"• sound_{aid}.ogg exists")

    print("🎉 All assets downloaded.")
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(port=8080)