# Up-Xel 🚀 — an arcade dodger built with Pygame

Collect coins, dodge blocks, race to the finish line. Classic one‑button fun — now with speed‑pads that boost or slow you down!

## Folder layout

* **main.py** – game entry point
* **images/** – backgrounds and GUI icons

  * **images/skins/** – 12 selectable player skins
  * **images/coin/** – 16‑frame spinning coin
  * **images/speedup/** – “^” tile animation
  * **images/speedown/** – “v” tile animation
* **sound/sfx/** – WAV effects
* **fonts/** – bundled TTFs
* **career/** – maps + default save file
* **build.spec** – PyInstaller recipe

## Controls

| Key              | Action                   |
| ---------------- | ------------------------ |
| Space            | start level / advance    |
| ← ↑ ↓ →  *(configurable)*         | move player 1            |
| *(configurable)* | pause, player 2 |

## Map legend (career/level files read bottom → top)

* `' '`  : empty space
* `'-'`  : finish line → win
* `'1'`  : solid block → death
* `'2'`  : coin → +1 coin
* `'^'`  : speed‑up pad → +50 % velocity
* `'v'`  : speed‑down pad → –50 % velocity

## Run from source

```bash
python -m pip install pygame psutil
python main.py
```

## Build portable Windows EXE

```bash
pip install pyinstaller
pyinstaller build.spec     # output lands in dist/Up-Xel/
```

All assets are bundled; a writable save‑file is created beside the exe on first run.

## License

MIT — see **LICENSE**.
