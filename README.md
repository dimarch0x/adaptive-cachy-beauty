<div align="center">
  <img src="resources/icons/icon.png" width="128" height="128" alt="Aurora Prism Icon" />
  <h1>Adaptive Cachy Beauty Engine</h1>
  <p><b>A beautiful, smart, and fully offline adaptive theming engine for CachyOS & KDE Plasma 6.6</b></p>

  <p>
    <a href="https://www.python.org/downloads/release/python-3120/"><img src="https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat&logo=python&logoColor=white" alt="Python 3.12+"></a>
    <a href="https://kde.org/plasma-desktop/"><img src="https://img.shields.io/badge/KDE_Plasma-6.x-1d99f3.svg?style=flat&logo=kde&logoColor=white" alt="KDE Plasma 6.x"></a>
    <a href="https://github.com/vinceliuice/Kvantum"><img src="https://img.shields.io/badge/Theme-Kvantum-ff69b4.svg?style=flat" alt="Kvantum Theme"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat" alt="License MIT"></a>
  </p>
</div>

---

## 📖 Overview

CachyOS is built for blistering speed and performance, but its stock Plasma themes can often feel slightly "gray" or disjointed. Does your environment lack that finishing touch?

**Adaptive Cachy Beauty Engine** solves this perfectly. It automatically analyzes your current wallpaper, extracts dominant colors using robust offline algorithms (Material You / ColorThief), and instantly generates a cohesive, readable color scheme. One click—or simply changing your wallpaper—and your entire desktop looks premium and dynamically styled, 24/7.

---

## ✨ Key Features

- 🎨 **Dynamic Styling Archetypes**
  Choose the mood that fits you best. Built-in styles include `Neon Glass`, `Frosted Glass`, `Material Pure`, `Vivid High-Contrast`, and `Soft Muted`.
- 🧠 **Smart Contrast Engine (HCT Delta)**
  Strict WCAG-compliant contrast checking. The engine intelligently shifts color tones to guarantee that text, window borders, and active panels remain perfectly readable, regardless of the wallpaper's complexity. You are in control of the level (`Standard`, `High`, `Medium`).
- 🪟 **True Glassmorphism**
  Automatic manipulation of `background_blur` and terminal `opacity` natively aligned with your chosen generation style.
- 🧩 **Comprehensive Ecosystem Integration**
  Your palette seamlessly penetrates every layer:
  - **KDE Plasma 6**: Semantic color mapping (Window, View, Button, Titlebars, Window Manager).
  - **Kvantum**: SVG-template re-coloring on the fly.
  - **Kitty & Alacritty**: Hot-reloading of ANSI 16-color terminal themes.
  - **Fish & Zsh**: Injection of universal modern shell variables.
- 🎛️ **Premium Settings UI**
  A beautiful, dark-themed, glassmorphic settings dialog featuring the custom *Aurora Prism* icon.
- 🔒 **100% Offline & Private**
  No cloud APIs. Image processing is done entirely locally via Colorthief and MaterialYouColor.

---

## 📸 Screenshots

*(Replace these placeholder links with your actual setup screenshots once deployed)*

| Dark Neon Glass | Soft Muted Mode |
| :---: | :---: |
| ![Dark Neon Glass Placeholder](https://via.placeholder.com/600x400/1e1e2e/89dceb?text=Dark+Neon+Glass+Theme) | ![Soft Muted Placeholder](https://via.placeholder.com/600x400/313244/f5e0dc?text=Soft+Muted+Theme) |
| *Vibrant terminal transparency with dynamic active borders.* | *Calm pastel tones ensuring high readability for deep focus.* |

---

## 🏗 Architecture

The engine is engineered for modularity and ease of extension:

```text
src/
├── core/
│   ├── theme_generator.py        # HCT / Material You color processing
│   └── wallpaper_analyzer.py     # Captures current KDE Plasma wallpaper
├── integrations/
│   ├── plasma_theme_manager.py   # Maps and applies KDE .colors files
│   ├── kvantum_generator.py      # Automates Kvantum SVG config edits
│   └── terminal_theme_manager.py # Controls Kitty, Alacritty, Fish, Zsh
├── ui/
│   └── settings_dialog.py        # The premium PySide6 control panel
├── config_manager.py             # Persistent JSON state management
├── logger.py                     # Rotating standard & debug logging
└── main.py                       # Application entrypoint & System Tray
```

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have Python 3.12+ and the base KDE dependencies installed (`plasma-workspace`, `kvantum`).

### 2. Installation

Clone the repository and set up your virtual environment:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/adaptive-cachy-beauty.git
cd adaptive-cachy-beauty

# Create and activate your virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Running the Engine

Simply execute the launcher script or the main file:

```bash
./run.sh
# OR
python src/main.py
```

The app will silently launch into your system tray.

- Right-click the **Aurora Prism** icon ➔ **Settings...** to tweak your profiles.
- Select **Refresh Theme** to immediately re-sample your wallpaper.

### Debug Mode

If you need to investigate contrast pairings or DBus signals:

```bash
ACB_LOG_LEVEL=DEBUG ./run.sh
```

---

## 🗺️ Roadmap

- [x] **Phase 1-2**: Core GUI, System Tray, File observation.
- [x] **Phase 3**: Terminal integrators (Kitty, Alacritty, Fish) & Hot-reloading.
- [x] **Phase 4**: Styling Archetypes & Smart Contrast V2 Engine.
- [x] **Phase 5**: UI/UX Polish, refactored project structure, and robust logging.
- [ ] **Phase 6**: SDDM & Plymouth (Boot/Login Screen) theming.
- [ ] **Phase 7**: Vision-model integration (e.g., Moondream2) for deep semantic analysis of the wallpaper subject matter.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
