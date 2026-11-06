# Ringfall level sprites

Sprites for the two level themes: the olive **outpost** (military camp) and the purple **fortress** (alien world). They match the plates build’s file names and canvas sizes, and they assemble into the side-view scenes in `preview/`.

## What the repo actually renders

Ringfall is Godot **4.7.2**.

| Build | Where | Rendering |
| --- | --- | --- |
| Live root | `/` | 2.5D. `HaloMain` is a `Node3D`. Characters are procedural meshes from `HaloModels`, not PNG sprites. |
| Plates preview | `ringfall-plates-preview/` | 2D pixel art. Nearest texture filter. Viewport **1280×720**. This is the sprite pipeline. |

Plates level names, from `HaloLevel`:

- **outpost** — camp around `res://assets/plate_outpost.png`. The player (`HaloPlayer` / hero) and a marine stand here.
- **mission** — second area on `res://assets/plate_mission.png`. Grunts, the overgrowth barrier, then the alien champion.

`HaloSprites` loads single-frame textures from `res://assets/`. Idle and walk are separate images, not strips. Hero frames are **256×256** and must stay at Sprite2D scale 1. Grunt frames are **128×128**. Directions on disk: hero `down`, `up`, `left`, `right`; grunt `down` and `right` (the game mirrors the right frame).

The reference paintings are side views. These files keep that design (olive armored rifleman, slender purple spear alien, eagle tents, jeep, pines, gothic cyan-lit towers, mushrooms) and place the characters on the canvas sizes the plates scripts already request.

## Engine drop-in (`assets/*.png`)

Copy these over `res://assets/` in the plates project. Corners are transparent. Alpha is only 0 or 255.

| File | Canvas | Replaces |
| --- | --- | --- |
| `hero_{down,up,left,right}_{idle,walk}.png` | 256×256 | Player soldier. Left frames are mirrors of right. |
| `grunt_{down,right}_{idle,walk}.png` | 128×128 | Purple alien grunt. Down is the front view. Right is the spear profile. |
| `tent.png` | 256×192 | Eagle tent |
| `warthog.png` | 256×192 | Armed jeep |
| `sandbag_wall.png` | 64×32 | Sandbag pile |
| `supply_crate.png` | 64×64 | Crate stack |
| `flag.png` | 48×96 | Blue camp flag |
| `satellite_dish.png` | 96×96 | Dish tower |

`boss_grunt.png` (320×320 champion) and `marine_*.png` are unchanged in the exported build. `tile_*.png` ground tiles stay the opaque top-down set; the side-view pine is a new scene sprite, not a replacement for `tile_tree.png`.

## Scene sprites

Larger copies used to build the dioramas, same designs, not scaled to the tiny prop slots:

- `assets/levels/outpost/` — tent, jeep, sandbags, crates, pine, flag, dish, `soldier_idle`, `soldier_walk`, `soldier_front`
- `assets/levels/fortress/` — tower, spire, mushrooms, platform, bridge, flora, planet, `alien_idle`, `alien_walk`, `alien_front`

## Preview

From the repo root:

```bash
python3 verify/sprites_check.py
python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/preview/`.

- **Outpost** — soldier in the camp. Left/right arrows or A/D walk him along the dirt. He flips to face the direction he walks.
- **Fortress** — purple alien on the bridge. The alien patrols between the towers.
- Keys `1` and `2` switch scenes.

Stills: `preview/outpost.png`, `preview/fortress.png`. The playable page uses `preview/outpost-bg.png` and `preview/fortress-bg.png` (same scenes without the actors) plus the level sprites. `verify/render_previews.py` rebuilds those four images. `verify/sprites_check.py` checks canvas sizes, hard transparency, and that both stills show the soldier and the alien.
