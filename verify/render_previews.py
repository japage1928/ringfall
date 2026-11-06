#!/usr/bin/env python3
"""Composite the outpost and fortress dioramas from the level sprites.

Hard-edged drawing only: rectangles and nearest-neighbor blits, no filtered shapes.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ROOT / "preview"
W, H = 1280, 720


def load(rel: str) -> Image.Image:
    return Image.open(ASSETS / rel).convert("RGBA")


def tint(im: Image.Image, factor: float) -> Image.Image:
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * factor), int(g * factor), int(b * factor), a)
    return out


def blit(canvas: Image.Image, im: Image.Image, cx: int, feet: int) -> tuple[int, int]:
    """Place sprite so its horizontal center is cx and its bottom sits on feet."""
    x = int(cx - im.width / 2)
    y = int(feet - im.height)
    canvas.alpha_composite(im, (x, y))
    return x, y


def noise_band(draw: ImageDraw.ImageDraw, y0: int, y1: int, colors: list[tuple[int, int, int]], seed: int) -> None:
    # Deterministic speckles. No antialiasing.
    n = (y1 - y0) * 18
    for i in range(n):
        x = (seed * 1103515245 + i * 12345) % W
        y = y0 + ((seed * 97 + i * 17) % max(1, y1 - y0))
        c = colors[(i + seed) % len(colors)]
        s = 1 + ((i + seed) % 3 == 0)
        draw.rectangle((x, y, x + s, y + s), fill=c)


def surface_row(im: Image.Image, frac: float = 0.35) -> int:
    """First row that is mostly opaque: the walkable top of a platform."""
    w, h = im.size
    px = im.load()
    need = int(w * frac)
    for y in range(h):
        count = sum(1 for x in range(w) if px[x, y][3])
        if count >= need:
            return y
    return 0


def draw_outpost(with_soldier: bool = True, soldier_x: int = 520) -> Image.Image:
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    # Olive sky down to the ground line so the horizon is not a black gap.
    for y in range(508):
        t = y / 508
        r = int(86 + 30 * t)
        g = int(98 + 24 * t)
        b = int(68 + 12 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # Distant treeline.
    pine = load("levels/outpost/pine.png")
    far = tint(pine.resize((pine.width * 2 // 3, pine.height * 2 // 3), Image.Resampling.NEAREST), 0.55)
    for cx in (40, 180, 320, 980, 1120, 1260):
        blit(canvas, far, cx, 468)
    # Ground and cutaway.
    draw.rectangle((0, 500, W, 640), fill=(154, 118, 70, 255))
    noise_band(draw, 506, 636, [(176, 140, 86), (120, 88, 52), (90, 78, 62)], 3)
    draw.rectangle((0, 640, W, H), fill=(92, 62, 40, 255))
    noise_band(draw, 648, H - 8, [(70, 48, 32), (120, 90, 60), (60, 70, 40)], 9)
    # A few hard-edged stones on the dirt.
    for x, y, w, h in ((70, 560, 18, 12), (240, 590, 14, 10), (800, 570, 22, 12), (1100, 600, 16, 11)):
        draw.rectangle((x, y, x + w, y + h), fill=(110, 104, 96, 255))
        draw.rectangle((x, y, x + w, y + 3), fill=(150, 144, 132, 255))

    pine_l = pine
    blit(canvas, pine_l, 120, 508)
    blit(canvas, pine_l, 1188, 508)
    tent = load("levels/outpost/tent.png")
    blit(canvas, tent, 390, 508)
    blit(canvas, tent, 690, 508)
    blit(canvas, load("levels/outpost/crates.png"), 210, 508)
    blit(canvas, load("levels/outpost/jeep.png"), 900, 508)
    blit(canvas, load("levels/outpost/flag.png"), 1048, 508)
    blit(canvas, load("levels/outpost/dish.png"), 1168, 500)
    blit(canvas, load("levels/outpost/sandbags.png"), 390, 524)
    blit(canvas, load("levels/outpost/sandbags.png"), 650, 528)
    if with_soldier:
        # Foreground, in front of the sandbags, feet on the dirt.
        blit(canvas, load("levels/outpost/soldier_idle.png"), soldier_x, 556)
    return canvas


def draw_fortress(with_alien: bool = True, alien_x: int = 640) -> Image.Image:
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(H):
        t = y / H
        r = int(18 + 28 * t)
        g = int(8 + 6 * t)
        b = int(36 + 30 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # Stars.
    for i in range(180):
        x = (i * 97 + 13) % W
        y = (i * 53 + 7) % 460
        s = 1 if i % 5 else 2
        c = (230, 220, 255, 255) if i % 4 else (170, 190, 255, 255)
        draw.rectangle((x, y, x + s, y + s), fill=c)
    blit(canvas, load("levels/fortress/planet.png"), 118, 188)

    tower = load("levels/fortress/tower.png")
    spire = load("levels/fortress/spire.png")
    blit(canvas, tower, 250, 470)
    blit(canvas, spire, 1040, 470)
    blit(canvas, tower.resize((tower.width * 2 // 3, tower.height * 2 // 3), Image.Resampling.NEAREST), 620, 450)

    # Violet chasm in front of the tower bases.
    for y in range(500, H):
        t = (y - 500) / (H - 500)
        draw.line((180, y, 1100, y), fill=(int(90 + 80 * t), int(20 + 10 * t), int(140 + 40 * t), 255))
    for i in range(40):
        x = 220 + (i * 37) % 820
        y = 520 + (i * 19) % 160
        draw.rectangle((x, y, x + 2, y + 18), fill=(210, 140, 255, 255))

    platform = load("levels/fortress/platform.png")
    bridge = load("levels/fortress/bridge.png")
    plat_top = surface_row(platform, 0.28)
    bridge_top = surface_row(bridge, 0.22)
    blit(canvas, platform, 210, 640)
    blit(canvas, platform, 1070, 640)
    bx, by = blit(canvas, bridge, 640, 600)
    # Mushrooms sit on the platform tops.
    shrooms = load("levels/fortress/mushrooms.png")
    # platform bottom is 640, top surface is plat_top from the sprite top.
    plat_surface = 640 - platform.height + plat_top
    blit(canvas, shrooms, 250, plat_surface + 8)
    small = shrooms.resize((shrooms.width * 2 // 3, shrooms.height * 2 // 3), Image.Resampling.NEAREST)
    right_surface = 640 - platform.height + plat_top
    blit(canvas, small, 1040, right_surface + 6)
    flora = load("levels/fortress/flora.png")
    blit(canvas, flora, 90, 575)
    blit(canvas, flora, 1190, 575)
    bridge_surface = by + bridge_top
    if with_alien:
        alien = load("levels/fortress/alien_idle.png")
        blit(canvas, alien, alien_x, bridge_surface + 4)
    return canvas


def layout() -> dict:
    platform = load("levels/fortress/platform.png")
    bridge = load("levels/fortress/bridge.png")
    bridge_top = surface_row(bridge, 0.22)
    bridge_surface = 600 - bridge.height + bridge_top
    return {
        "width": W,
        "height": H,
        "outpost": {
            "ground": 508,
            "soldier": {
                "x": 520,
                "feet": 556,
                "minX": 90,
                "maxX": 1190,
                "idle": "levels/outpost/soldier_idle.png",
                "walk": "levels/outpost/soldier_walk.png",
            },
        },
        "fortress": {
            "bridgeSurface": bridge_surface + 4,
            "alien": {
                "x": 640,
                "feet": bridge_surface + 4,
                "minX": 520,
                "maxX": 760,
                "idle": "levels/fortress/alien_idle.png",
                "walk": "levels/fortress/alien_walk.png",
            },
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    info = layout()
    draw_outpost(False).save(OUT / "outpost-bg.png")
    draw_fortress(False).save(OUT / "fortress-bg.png")
    draw_outpost(True, info["outpost"]["soldier"]["x"]).save(OUT / "outpost.png")
    draw_fortress(True, info["fortress"]["alien"]["x"]).save(OUT / "fortress.png")
    (OUT / "layout.json").write_text(json.dumps(info, indent=2))
    print("wrote previews")
    print(info)


if __name__ == "__main__":
    main()
