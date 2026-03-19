# Troubleshooting Guide

## 1. 🖼️ SDDM Sync Not Working

**Symptoms:** Login screen background doesn't match desktop.
**Fix:**

- Ensure you have run the setup script: `sudo adaptive-cachy-sddm-setup` (or `sudo ./setup_sddm.sh`).
- Check if `/var/lib/adaptive-cachy/` exists and is writable by your user.
- Verify that the SDDM theme is set to `AdaptiveCachy` in System Settings.

## 2. 🌫️ Window Blur is Missing

**Symptoms:** Settings window is transparent but not blurry.
**Fix:**

- **Wayland:** KWin blur on Wayland requires the `_KDE_NET_WM_BLUR_BEHIND_REGION` property. The engine attempts this via `xprop` (XWayland compatibility). Ensure `xorg-xprop` is installed.
- **X11:** Blur should work automatically if Desktop Effects are enabled.
- Ensure "Blur" effect is enabled in KDE System Settings -> Desktop Effects.

## 3. 📡 DBus Connection Failures

**Symptoms:** Wallpaper changes are not detected.
**Fix:**

- Check logs: `tail -f ~/.cache/adaptive-cachy-beauty/app.log`.
- Look for `Successfully connected to Plasma DBus`.
- If it fails, ensure `plasmashell` is running and the DBus session bus is active.

## 4. 🎨 Konsole/Terminal Not Updating

**Fix:**

- Ensure "Enable Terminal Sync" is checked in Preferences.
- For **Zsh/Fish**, you might need to reload your shell or source the generated color scripts in your `.zshrc` / `config.fish`.
- The engine creates `~/.cache/adaptive-cachy-beauty/colors.sh`. Source this in your shell config.
