# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1-beta] - 2026-03-21

### Fixed

- **Plasma Kornerbug**: Radically resolved X11 architectural limits with KWin blur by introducing a dynamic glassmorphism radius (0px for Glass modes, 16px for Solid modes).
- Perfect pristine Glass rendering without broken shader complexity or visual corner steps.
- Fixed trailing whitespace violations in test files picked up by Ruff CI pipeline.

## [1.0.0] - 2026-03-19

### Added

- **Full SDDM Integration**: Added QML theme, `setup_sddm.sh` helper, and daemon synchronization
- **Advanced Documentation**: Created `ARCHITECTURE.md` and `TROUBLESHOOTING.md` in `docs/`
- **Packaging**: Added `PKGBUILD` for Arch Linux (AUR) distribution support
- **Asset Library**: New premium icons (`shield.svg`, `monitor.svg`, `terminal-icon.svg`) and preview textures
- **CI/CD Infrastructure**: Added `dependabot.yml` and unified GitHub Actions pipeline
- **Dynamic Light Theme**: Implemented real-time QSS interpolation for all settings widgets
- **UI Persistence**: Added `cached_palette` to `config.json` for zero-delay rendering on launch
- **Refined Layout**: New About section with GitHub integration and capsule-style UI borders
- Premium Glassmorphism with animated frost overlay and adaptive blur per style
- Auto (Smart) theme style selection based on wallpaper HCT tone/chroma
- SDDM Login Screen integration with zero-sudo daily synchronization
- Custom Glassmorphism SDDM theme (QML-based)
- GitHub Actions CI pipeline with headless PySide6 testing
- Community Standards: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- Issue and Pull Request templates
- CODEOWNERS for automated review assignment
- CI status badge and Coverage badge (41%) in README
- Ruff linting in CI pipeline

### Fixed

- Config defaults now include `enable_terminals`, `enable_sddm`, and `theme_style`
- Settings UI colors now dynamically update when theme changes in the background
- Test wallpaper asset bundled locally (no more system path dependency)
- `YOUR_GITHUB_USERNAME` placeholder replaced in README
- Removed `score.txt` and `.coverage` from repository tracking

## [0.5.0-beta] - 2026-03-18

### Added

- Smart Contrast Engine with HCT Delta for WCAG-compliant readability
- Three theme styles: Neon Glass, Frosted Glass, Material Pure
- Terminal theming for Kitty, Alacritty, Fish, and Zsh
- Kvantum SVG theme generation
- KDE Plasma color scheme generation with semantic mapping
- Wallpaper-reactive DBus listener with 2s debounce
- System tray application with Settings UI
- QSS stylesheet extraction for maintainable UI theming
- pytest-qt integration tests for Settings Dialog

### Fixed

- Dolphin pathbar and active window title readability via tone-mapped pairs
- Terminal blur/opacity profiles per theme style

[1.0.0]: https://github.com/dimarch0x/adaptive-cachy-beauty/compare/v0.5.0-beta...v1.0.0
[0.5.0-beta]: https://github.com/dimarch0x/adaptive-cachy-beauty/releases/tag/v0.5.0-beta
