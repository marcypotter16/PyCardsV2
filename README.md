🃏 Card Game (Pygame)

A 2D card game built with Python and Pygame, featuring resolution-independent rendering, scalable UI, and a clean game-state architecture.

This project is primarily focused on:

Correct handling of multiple resolutions and aspect ratios

Clean separation between game logic and rendering

Smooth card rendering and zooming without distortion

✨ Features

🎴 Card-based gameplay

🖥️ Resolution-independent rendering using a logical game canvas

📐 Automatic scaling with letterboxing (no stretching)

🖱️ Correct mouse input mapping (screen → game coordinates)

🔄 State stack system (menus, gameplay, overlays)

⚙️ Configurable settings (resolution, FPS)

📸 Rendering Architecture (Overview)

The game uses a fixed logical resolution for all game logic and rendering:

Game World (logical resolution)
        ↓ scale
Screen (actual window size)


All gameplay is rendered to an off-screen game canvas

The canvas is scaled uniformly to fit the window

Black bars (letterboxing) are used if aspect ratios differ

Mouse input is transformed back into game coordinates

This ensures:

No stretching

Consistent positioning

Clean scaling at any resolution

🛠️ Requirements

Python 3.10+ (recommended)

Pygame 2.0+

Install dependencies:

pip install pygame

▶️ Running the Game

Clone the repository and run:

python main.py


(Replace main.py with your actual entry point if different.)

📁 Project Structure (simplified)
.
├── assets/          # Card images, fonts, sounds
├── states/          # Game states (menu, gameplay, etc.)
├── core/
│   ├── renderer.py  # Scaling & rendering logic
│   ├── settings.py  # GameSettings class
│   └── input.py     # Mouse / input helpers
├── main.py          # Game entry point
└── README.md

⚙️ Settings

Game settings are handled via a GameSettings class and can be serialized to JSON.

Example options:

Logical game resolution

Window resolution

Target FPS

This makes it easy to add:

Config files

Settings menus

Resolution switching

🚧 Status

This project is under active development.
Gameplay, visuals, and features are still evolving.

Expect:

Refactors

API changes

Placeholder assets

🧠 Notes for Developers

All game logic uses game-space coordinates

Never use screen coordinates directly for gameplay

Rendering and input both go through the same transform logic

Scaling happens once per frame, surface allocation only on resize

📜 License

MIT License (or replace with your preferred license).

🙌 Acknowledgements

Built with Pygame

Inspired by classic digital card games and clean 2D engine design