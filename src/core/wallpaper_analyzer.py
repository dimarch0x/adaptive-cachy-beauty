import subprocess
import shutil

from logger import logger


class WallpaperAnalyzer:
    def __init__(self):
        self.qdbus_cmd = self._find_qdbus()
        if not self.qdbus_cmd:
            logger.error(
                "Could not find qdbus executable (qdbus6, qdbus-qt6, or qdbus). KDE integration will fail."
            )
        else:
            logger.debug(f"Found qdbus executable: {self.qdbus_cmd}")

    def _find_qdbus(self) -> str:
        """Finds the correct qdbus command for the system (Plasma 6 usually uses qdbus6 or qdbus-qt6)"""
        for cmd in ["qdbus-qt6", "qdbus6", "qdbus"]:
            if shutil.which(cmd):
                return cmd
        return ""

    def get_current_wallpaper_path(self) -> str:
        """Retrieves the current wallpaper path via Plasma 6 DBus script."""
        if not self.qdbus_cmd:
            return ""

        logger.debug("Running DBus query to get active wallpaper...")
        try:
            # We use org.kde.PlasmaShell.wallpaper to get current wallpaper for screen 0
            # This handles slideshows correctly as well.
            result = subprocess.run(
                [
                    self.qdbus_cmd,
                    "org.kde.plasmashell",
                    "/PlasmaShell",
                    "org.kde.PlasmaShell.wallpaper",
                    "0",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Find the 'Image:' line in the output
            wallpaper_path = ""
            for line in result.stdout.split("\n"):
                if line.startswith("Image:"):
                    wallpaper_path = line.split(":", 1)[1].strip()
                    break

            output = wallpaper_path
            logger.debug(f"DBus Output: {wallpaper_path}")

            # The output might start with 'file://'
            if output.startswith("file://"):
                output = output[7:]

            return output.strip()
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error executing dbus script: {e}")
            return ""
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ""


if __name__ == "__main__":
    # Test execution
    analyzer = WallpaperAnalyzer()
    path = analyzer.get_current_wallpaper_path()
    print(f"Current wallpaper path: {path}")
