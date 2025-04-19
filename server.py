from flask import Flask, request, jsonify
import os, json, requests

app = Flask(__name__)
EXPORT_DIR = "exports"
MODEL_DIR  = os.path.join(EXPORT_DIR, "models")
TEX_DIR    = os.path.join(EXPORT_DIR, "textures")
ANIM_DIR   = os.path.join(EXPORT_DIR, "animations")
CHAR_DIR   = os.path.join(MODEL_DIR, "characters")

for d in (EXPORT_DIR, MODEL_DIR, TEX_DIR, ANIM_DIR, CHAR_DIR):
    os.makedirs(d, exist_ok=True)

def download_asset(aid, dest):
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={aid}"
    print(f"→ Downloading asset {aid} to {dest}…", end="")
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
    data        = request.get_json()
    models      = data.get("models", [])
    textures    = data.get("textures", [])
    animations  = data.get("animations", [])
    characters  = data.get("characters", [])

    print("🔄 Received assets payload:")
    print(f"   • {len(models)} model refs")
    print(f"   • {len(textures)} texture refs")
    print(f"   • {len(animations)} animations")
    print(f"   • {len(characters)} character entries")

    # --- Download mesh assets ---
    for idx, m in enumerate(models, start=1):
        if isinstance(m, str):
            aid = "".join(filter(str.isdigit, m))
            dest = os.path.join(MODEL_DIR, f"mesh_{aid}.fbx")
            if not os.path.exists(dest):
                try:
                    download_asset(aid, dest)
                except Exception as e:
                    print(f"✖️ Failed mesh {aid}:", e)
            else:
                print(f"• Mesh {aid} already exists, skipping.")
        else:
            name = f"prim_{m['primitive']}_{m['size'][0]}x{m['size'][1]}x{m['size'][2]}.json"
            dest = os.path.join(MODEL_DIR, name)
            with open(dest, "w") as f:
                json.dump(m, f)
            print(f"✔️ Wrote primitive descriptor → {name}")

    # --- Download textures ---
    for idx, t in enumerate(textures, start=1):
        aid = "".join(filter(str.isdigit, t))
        dest = os.path.join(TEX_DIR, f"tex_{aid}.png")
        if not os.path.exists(dest):
            try:
                download_asset(aid, dest)
            except Exception as e:
                print(f"✖️ Failed texture {aid}:", e)
        else:
            print(f"• Texture {aid} already exists, skipping.")

    # --- Download animations ---
    for idx, a in enumerate(animations, start=1):
        aid = "".join(filter(str.isdigit, a))
        dest = os.path.join(ANIM_DIR, f"anim_{aid}.rbxanim")
        if not os.path.exists(dest):
            try:
                download_asset(aid, dest)
            except Exception as e:
                print(f"✖️ Failed animation {aid}:", e)
        else:
            print(f"• Animation {aid} already exists, skipping.")

    # --- Download character parts ---
    for cidx, char in enumerate(characters, start=1):
        cname = char["name"]
        cdir  = os.path.join(CHAR_DIR, cname)
        os.makedirs(cdir, exist_ok=True)
        print(f"— Processing character '{cname}' ({cidx}/{len(characters)}) —")
        for pidx, part in enumerate(char["parts"], start=1):
            if "meshId" in part:
                aid = "".join(filter(str.isdigit, part["meshId"]))
                dest = os.path.join(cdir, f"mesh_{aid}.fbx")
                if not os.path.exists(dest):
                    try:
                        download_asset(aid, dest)
                    except Exception as e:
                        print(f"✖️ Failed char mesh {aid}:", e)
                else:
                    print(f"• Char mesh {aid} exists, skipping.")
            else:
                name = f"prim_{part['primitive']}_{part['size'][0]}x{part['size'][1]}x{part['size'][2]}.json"
                dest = os.path.join(cdir, name)
                with open(dest, "w") as f:
                    json.dump(part, f)
                print(f"✔️ Wrote char primitive → {name}")

    print("🎉 Asset download complete.")
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(port=8080)