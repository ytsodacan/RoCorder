# Roblox Replay Exporter to Blender

This project captures Roblox gameplay and assets, then exports them to a `.soda` format and associated model folders — all of which can be imported into **Blender** for replay visualization, editing, and animation.

---

## Features

### Roblox Client (Lua)
- Records **player positions** over time (press `E` to toggle recording).
- Sends map and replay data to a Python server (press `R`).
- Extracts:
  - All **3D parts and models**
  - **MeshParts** and primitive parts
  - **Textures** and decals
  - **Player characters**, including hats/accessories
  - **Animations** (walking, idle, etc.)
- Keybinds:
  - `E` → Start/stop recording
  - `R` → Send replay to server
  - `M` → Send all models, assets, textures to server

### Python Flask Server
- Listens for `/record` and `/assets` POSTs
- Saves:
  - `recorded_data.soda`: JSON timeline of player motion and world layout
  - `models/`: `.fbx` MeshParts + JSON primitives
  - `textures/`: downloaded `.png` images
  - `animations/`: `.rbxanim` files
  - `models/characters/`: individual player rigs and meshes

### Blender Integration
- Python script to import the `.soda` file and build a scene:
  - Imports `.fbx` meshes and textures
  - Builds player rigs from `.rbxanim`
  - Applies camera and animation keyframes from recording
  - Final scene shows full replay with map and player motion

---

## Folder Structure
.
├── exports/
│   ├── recorded_data.soda
│   ├── models/
│   │   ├── mesh_.fbx
│   │   ├── prim_.json
│   │   └── characters/
│   │       └── /…
│   ├── textures/
│   │   └── tex_.png
│   └── animations/
│       └── anim_.rbxanim
├── asset_server.py
├── import_soda_to_blender.py
└── README.md
---

## Pipeline

1. **Run Python Server**
   ```bash
   pip install flask requests
   python asset_server.py
2.	Run Roblox in Play Mode
	•	Press M → sends map + asset data to /assets
	•	Press E → start recording
	•	Press E again → stop recording
	•	Press R → sends recorded frames to /record
	3.	Open Blender
	•	Run import_soda_to_blender.py to import everything
	•	See a visual replay of the recorded scene

⸻

Requirements
	•	Roblox Studio
	•	Python 3.8+
	•	Blender (with rbx2blender or FBX importer add-on)

⸻

To Do
	•	Improve texture/material mapping in Blender
	•	Add camera interpolation
	•	UI inside Blender for choosing which replay to load
