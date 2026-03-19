# Contributing to Adaptive Cachy Beauty

Thank you for your interest in contributing to **Adaptive Cachy Beauty**! 🚀
This project is built to bring dynamic, automated glassmorphism and WCAG-compliant styling to CachyOS and KDE Plasma. We welcome all contributions, from bug fixes to new theme archetypes!

## 1. Local Development Setup

To test changes locally, you need a Python environment and standard KDE tools.

```bash
git clone https://github.com/dimarch0x/adaptive-cachy-beauty.git
cd adaptive-cachy-beauty

# Create an isolated environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Run the application locally (it will place an icon in your system tray):

```bash
./run.sh
```

## 2. Project Architecture Overview

We strictly separate our logic for highly maintainable code:

- `src/core/`: The math and extraction layer (`theme_generator.py`, `wallpaper_analyzer.py`).
- `src/integrations/`: Applies colors to specific tools (`plasma_theme_manager.py`, `terminal_theme_manager.py`).
- `src/ui/`: PySide6 settings user interfaces.

*Do not mix UI code with core generation logic.*

## 3. King Swarm Coding Standards

We enforce a few strict rules (inspired by our internal King Swarm directives):

- **Aesthetic Excellence:** If you are modifying the UI, it must look "wow" at first glance. Generic designs are unacceptable. Use HSL tuning, dark modes, and dynamic animations where appropriate.
- **Type Hints:** Use standard Python type hinting for function signatures (`def do_magic(value: int) -> str:`).
- **Conventional Commits:** Your commit messages MUST follow the standard:
  - `feat:` for new features.
  - `fix:` for bug fixes.
  - `refactor:` for code restructuring.
  - `docs:` for documentation updates.
  - `test:` for adding or updating tests.

## 4. Testing

Before submitting a Pull Request, ensure our `pytest` suite passes:

```bash
./venv/bin/pytest tests/
```

If you add a new integration or feature, please include a test for it or ask the maintainers for help.

## 5. Pull Request Process

1. Fork the repository and create your branch from `master`.
2. Push your commits following the [Conventional Commits](#3-king-swarm-coding-standards) format.
3. Open a Pull Request referencing any related open Issues.
4. We will review your code as soon as possible!
