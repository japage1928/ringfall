#!/usr/bin/env python3
"""Check Ringfall sprite canvases, hard alpha, and the two level previews."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Godot plates pipeline (HaloSprites / res://assets). Exact canvas sizes, unscaled.
ENGINE = {
    "hero_down_idle.png": (256, 256),
    "hero_down_walk.png": (256, 256),
    "hero_up_idle.png": (256, 256),
    "hero_up_walk.png": (256, 256),
    "hero_left_idle.png": (256, 256),
    "hero_left_walk.png": (256, 256),
    "hero_right_idle.png": (256, 256),
    "hero_right_walk.png": (256, 256),
    "grunt_down_idle.png": (128, 128),
    "grunt_down_walk.png": (128, 128),
    "grunt_right_idle.png": (128, 128),
    "grunt_right_walk.png": (128, 128),
    "tent.png": (256, 192),
    "warthog.png": (256, 192),
    "sandbag_wall.png": (64, 32),
    "supply_crate.png": (64, 64),
    "flag.png": (48, 96),
    "satellite_dish.png": (96, 96),
}

SCENE = [
    "levels/outpost/tent.png",
    "levels/outpost/jeep.png",
    "levels/outpost/sandbags.png",
    "levels/outpost/crates.png",
    "levels/outpost/pine.png",
    "levels/outpost/flag.png",
    "levels/outpost/dish.png",
    "levels/outpost/soldier_idle.png",
    "levels/outpost/soldier_walk.png",
    "levels/outpost/soldier_front.png",
    "levels/fortress/tower.png",
    "levels/fortress/spire.png",
    "levels/fortress/mushrooms.png",
    "levels/fortress/platform.png",
    "levels/fortress/bridge.png",
    "levels/fortress/flora.png",
    "levels/fortress/planet.png",
    "levels/fortress/alien_idle.png",
    "levels/fortress/alien_walk.png",
    "levels/fortress/alien_front.png",
]


def fail(msg: str) -> None:
    print("FAIL", msg)
    raise SystemExit(1)


def is_magenta_leak(r: int, g: int, b: int) -> bool:
    return g < 40 and r > 185 and b > 100 and r > b


def check_image(path: Path, size: tuple[int, int] | None, min_opaque: int, clear_corners: bool) -> None:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    im = Image.open(path)
    if im.mode != "RGBA":
        fail(f"{path.name} mode {im.mode}, expected RGBA")
    if size and im.size != size:
        fail(f"{path.name} size {im.size}, expected {size}")
    hist = im.getchannel("A").histogram()
    partial = sum(hist[1:255])
    if partial:
        fail(f"{path.name} has {partial} partial-alpha pixels")
    opaque = hist[255]
    if opaque < min_opaque:
        fail(f"{path.name} only {opaque} opaque pixels")
    if clear_corners:
        px = im.load()
        w, h = im.size
        for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            if px[x, y][3] != 0:
                fail(f"{path.name} corner {(x, y)} is not transparent")
    leaks = 0
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and is_magenta_leak(r, g, b):
                leaks += 1
    if leaks:
        fail(f"{path.name} has {leaks} magenta-key leaks")
    print(f"ok {path.relative_to(ROOT)} {im.size} opaque={opaque}")


def check_scenes() -> None:
    sys.path.insert(0, str(ROOT / "verify"))
    import render_previews

    render_previews.main()
    outpost = Image.open(ROOT / "preview" / "outpost.png").convert("RGBA")
    fortress = Image.open(ROOT / "preview" / "fortress.png").convert("RGBA")
    if outpost.size != (1280, 720) or fortress.size != (1280, 720):
        fail("preview size is not 1280x720")
    # Horizon must be the olive sky, not the black canvas showing through.
    sky = outpost.getpixel((8, 450))
    if sky[1] < 70 or sky[0] < 40:
        fail(f"outpost horizon is not olive sky: {sky}")
    # Soldier stands on the dirt in front of the tents: sample his torso.
    torso = outpost.getpixel((520, 500))
    if torso[1] < 60:
        fail(f"soldier torso missing at outpost (520, 500): {torso}")
    # Alien body is the purple mass on the bridge, just right of the spear.
    found_alien = False
    fpx = fortress.load()
    for y in range(330, 430):
        for x in range(640, 710):
            r, g, b, _a = fpx[x, y]
            if r > 120 and b > 150 and g < 130:
                found_alien = True
                break
        if found_alien:
            break
    if not found_alien:
        fail("alien body not visible on the fortress bridge")
    # Background plates used by the playable page omit the actors.
    bg = Image.open(ROOT / "preview" / "outpost-bg.png").convert("RGBA")
    if bg.getpixel((520, 500)) == torso:
        fail("outpost background still has the soldier baked in")
    print("ok scenes outpost + fortress")


def main() -> None:
    for name, size in ENGINE.items():
        check_image(ASSETS / name, size, min_opaque=80, clear_corners=True)
    for rel in SCENE:
        check_image(ASSETS / rel, None, min_opaque=200, clear_corners=False)
    check_scenes()
    print("SPRITES OK")


if __name__ == "__main__":
    main()
