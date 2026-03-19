# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

[Unreleased]: https://github.com/dimarch0x/adaptive-cachy-beauty/compare/v0.5.0-beta...HEAD
[0.5.0-beta]: https://github.com/dimarch0x/adaptive-cachy-beauty/releases/tag/v0.5.0-beta
