# Up-Xel 🚀 — an arcade dodger built with Pygame

Collect coins, dodge blocks, and survive until you hit finish line.

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

## Default Controls *(configurable)*  

| Key              | Action                   |
| ---------------- | ------------------------ |
| Space            | start level / advance    |
| ← ↑ ↓ →          | move player 1            |
| Other            | pause, player 2 |

## Map legend (career/level files read bottom → top)

* `' '`  : empty space
* `'-'`  : finish line → win
* `'1'`  : solid block → death
* `'2'`  : coin → +1 coin
* `'^'`  : speed‑up pad
* `'v'`  : speed‑down pad

## Run from source

python -m pip install pygame psutil
python main.py

All assets are bundled; a writable save‑file is created beside the exe on first run.
