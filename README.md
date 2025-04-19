# RoCorder
	•	Client‑side Lua Scripts
	•	ReplayAndAssetClient.lua (StarterPlayerScripts)
	•	E to start/stop recording player frames
	•	R to send map + frame data to the server (/record)
	•	M to gather every MeshPart, primitive, decal, texture, animation, and full character model (with cosmetics), then fire to /assets
	•	On‑screen status GUI showing recording state and frame count
	•	Debounced keypresses and chunked frame uploads for reliability
	•	Server‑side Lua Script
	•	ReplayAndAssetServer.lua (ServerScriptService)
	•	Listens to RecordEvent and AssetEvent, forwards JSON payloads to your Python server
	•	Python Flask Server
	•	asset_server.py
	•	/record endpoint: writes out recorded_data.soda JSON
	•	/assets endpoint: downloads into exports/models/, exports/textures/, exports/animations/, and exports/models/characters/
	•	Handles both external MeshPart FBX and primitive descriptors, textures (PNG), animations (.rbxanim), and per‑player character models
	•	Blender Import Script
	•	import_soda_to_blender.py
	•	Clears the scene, imports FBX meshes and primitives, loads textures
	•	Imports .rbxanim via a Roblox → Blender add‑on (e.g. rbx2blender)
	•	Imports each player’s character model and parents parts under an Empty
	•	Reads recorded_data.soda, positions map parts, rigs up animation keyframes for player empties
	•	Scene end‑frame matches replay length
	•	Exported Data Format
	•	.soda JSON containing:
	•	map: array of part descriptors
	•	frames: timestamped player root‐motion frames
	•	exports/ folder structure:
 exports/
  recorded_data.soda
  models/            # mesh_*.fbx + prim_*.json
  textures/          # tex_*.png
  animations/        # anim_*.rbxanim
  models/characters/ # per‑player model parts
  •	Zero Dependencies in Roblox (uses only built‑in services)
	•	Cross‑platform Blender import (runs headless or in‑UI)

⸻

Pipeline Overview
	1.	Start Python Server
 pip install flask requests
python asset_server.py
Listens on localhost:8080 for /record and /assets.

	2.	In‑Game
	•	Press M → client gathers MeshParts, primitives, decals, textures, animation tracks, full character models → fires AssetEvent → server‑script → POST /assets → downloads everything into exports/.
	•	Press E → toggles recording; captures each frame’s root CFrame.
	•	Press R → client fires RecordEvent with map + all frames → server → POST /record → writes exports/recorded_data.soda.
 3.	Verify exports/ Folder
    exports/
  recorded_data.soda      ← your recorded map+frames
  models/                 ← .fbx and .json primitives
  textures/               ← .png textures
  animations/             ← .rbxanim files
  models/characters/      ← per‑player FBX or json
4.	Blender Import
	•	Open Blender (ensure Roblox add‑on installed).
	•	Run import_soda_to_blender.py (Scripting tab or blender --background --python ...).
	•	Scene is built: map parts, textured meshes, animated player rigs (with cosmetics), plus skeletal animations.
