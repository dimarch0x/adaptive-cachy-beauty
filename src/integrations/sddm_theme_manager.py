import os
import shutil
import configparser
from logger import logger

class SddmThemeManager:
    """
    Manages synchronization of the current wallpaper and color palette to the SDDM theme.
    Relies on /var/lib/adaptive-cachy/ being writable by the current user (configured via setup_sddm.sh).
    """
    def __init__(self):
        self.config_dir = "/var/lib/adaptive-cachy"
        self.colors_file = os.path.join(self.config_dir, "theme.conf")
        self.bg_file = os.path.join(self.config_dir, "background.jpg")

    def _rgb_from_hex(self, hex_color: str) -> str:
        return hex_color

    def apply_to_sddm(self, wallpaper_path: str, palette: dict, theme_style: str):
        if not os.path.exists(self.config_dir):
            logger.warning(f"Wait: {self.config_dir} not found. SDDM integration skipped. Run `sudo ./setup_sddm.sh` to enable.")
            return

        # 1. Copy background
        if os.path.exists(wallpaper_path):
            try:
                shutil.copy2(wallpaper_path, self.bg_file)
                logger.debug(f"Copied {wallpaper_path} to {self.bg_file}")
            except Exception as e:
                logger.error(f"Failed to copy wallpaper for SDDM: {e}")

        # 2. Write theme.conf variables
        try:
            config = configparser.ConfigParser()
            config.optionxform = str

            config["General"] = {
                "background": self.bg_file,
                "type": "image",
                "primary": palette.get("primary", "#ffffff"),
                "on_primary": palette.get("on_primary", "#000000"),
                "primary_container": palette.get("primary_container", "#aaaaaa"),
                "on_primary_container": palette.get("on_primary_container", "#ffffff"),
                "secondary": palette.get("secondary", "#888888"),
                "background_color": palette.get("background", "#000000"),
                "on_background": palette.get("on_background", "#ffffff"),
                "surface": palette.get("surface", "#111111"),
                "surface_variant": palette.get("surface_variant", "#222222"),
                "error": palette.get("error", "#ff0000")
            }

            with open(self.colors_file, "w") as f:
                config.write(f)
            logger.info("SDDM theme configuration updated seamlessly.")
        except Exception as e:
            logger.error(f"Failed to write SDDM colors: {e}")
