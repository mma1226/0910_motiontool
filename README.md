# 0910_motiontool — Cube Motion Rig

A motion tool for the hex-dither isometric cube (`cube.svg`). Open `cube-motion.html`
in a browser — no build step, no dependencies, no server. Everything is inlined.

Live copy: https://claude.ai/code/artifact/52d90599-de58-4be5-bb83-01b7d8162bc7
(the hosted version asks for confirmation on each save; the local file just downloads).

## What it does

The source SVG is 1,724 hexagonal tiles scattered along the nine visible edges of an
isometric cube, in six tones. The rig recovers the geometry those tiles imply and
animates in **cube space rather than screen space**, so a sweep along the Z axis
crosses the left and right faces in the right order, and displacement pushes each
tile out along its own face normal.

Per tile, `build/extract.py` recovers:

| field | meaning |
| --- | --- |
| `X, Y, Z` | position on the cube surface in `[0,1]`, by inverting the isometric projection per face |
| `face` | 0 top (Z=1), 1 left (Y=1), 2 right (X=1) |
| `edge`, `t` | nearest of the 9 visible wireframe edges, and position along it |
| `shape`, `color` | index into the deduped path table and the six-tone palette |

Recentering every path on its own tile collapses 1,724 paths into 269 distinct shapes,
which is what makes a canvas renderer cheap: ~0.6 ms/frame, so 60 fps capture is real.

## Using it

Two modes. **Pulse** loops a travelling wave; **Build** runs a one-shot entrance or exit.
Eight presets — Corner ripple, Edge trace, Face sweep, Dither bloom, Idle shimmer,
Assemble, Settle, Scatter — are starting points, not the whole range: order can key off
the near corner, the top vertex, the wireframe path, any cube axis, face, **tone**
(the dither's own dark-to-light ramp), a screen sweep at any angle, or random.

Export: WebM/MP4 of one loop, PNG of the current frame, the settings as JSON, or
**Export player** — a self-contained HTML file playing just that one animation, built by
serializing the same render functions the tool uses, so an export can't drift from its
preview. Drop it in a page as an iframe or a full-bleed background.

WebM has no usable alpha: record on Void or Paper. The Alpha ground is for PNG frames
and for the exported player, which is genuinely transparent.

## Rebuilding

```bash
python3 build/extract.py   # cube.svg  -> build/tiles.json
python3 build/make.py      # tiles.json + build/app.tpl.html -> cube-motion.html
```

`build/app.tpl.html` is the only file to edit by hand; `cube-motion.html` is generated
(the data is substituted for `__DATA__`). `make.py` also writes `build/artifact.html`,
the same page without the document wrapper, for publishing — it is gitignored.
