# Technical Architecture

Adaptive Cachy Beauty is a modular adaptive theming engine designed for KDE Plasma and Arch-based distributions (like CachyOS). This document explains the internal logic and design decisions.

## 🎨 Color Science: HCT vs RGB

Most theming engines use simple RGB/HSL models, which often lead to unreadable text on bright backgrounds. We use **Material You (HCT)**:

- **Hue:** The "color" (red, blue, green).
- **Chroma:** The "vividness" or saturation.
- **Tone:** The **Perceptual Brightness**. This is the most critical part.

Our **Smart Contrast Engine** calculates the HCT Tone difference between the background and foreground. We enforce a minimum **Delta Tone** (usually 50-60) to guarantee WCAG-compliant readability, regardless of the wallpaper's colors.

## 🧠 Smart Style Heuristics

The "Auto (Smart)" mode replaces heavy ML models with an algorithmic approach:

1. **Extract Palette:** Uses ColorThief and QuantizeCelebi.
2. **Mood Analysis:**
    - If `background_tone < 40` AND `primary_chroma > 40` -> **Neon Glass**.
    - If `40 <= tone <= 70` AND `chroma < 30` -> **Frosted Glass**.
    - Otherwise -> **Material Pure**.

## 🔄 SDDM Integration (Zero-Sudo Architecture)

Standard SDDM themes require root to change colors/wallpapers. We solve this via a world-readable sync directory:

1. **One-time setup:** `/var/lib/adaptive-cachy/` is created and owned by the current user.
2. **Runtime:** The Python daemon writes `theme.conf` and copies the wallpaper to this folder.
3. **QML:** The SDDM theme (`AdaptiveCachy`) reads directly from this folder at boot time.

## 🛠️ Integration Layers

- **KDE Plasma:** Generates `.colors` schemes and applies them via `plasma-apply-colorscheme`.
- **Kvantum:** Generates an SVG-based theme and updates `kvantummanager`.
- **Terminals:** Updates Kitty/Alacritty config files using regex pattern matching.
- **Stylescripts:** Updates Fish/Zsh syntax highlighting colors.
