import os
import subprocess
import shutil
from logger import logger


class KvantumGenerator:
    def __init__(self, base_theme_name="KvFlat"):
        self.base_theme_name = base_theme_name
        self.base_theme_dir = f"/usr/share/Kvantum/{base_theme_name}"
        self.target_theme_name = "AdaptiveCachy"
        self.target_dir = os.path.expanduser(
            f"~/.config/Kvantum/{self.target_theme_name}"
        )

    def generate_and_apply(self, palette: dict):
        """Generates a Kvantum theme config from the given palette and applies it."""
        try:
            os.makedirs(self.target_dir, exist_ok=True)

            # 1. Copy SVG from base if not exists
            svg_source = os.path.join(
                self.base_theme_dir, f"{self.base_theme_name}.svg"
            )
            svg_target = os.path.join(self.target_dir, f"{self.target_theme_name}.svg")

            if not os.path.exists(svg_target):
                logger.debug(f"Copying basic SVG from {svg_source} to {svg_target}")
                shutil.copy2(svg_source, svg_target)

            # 2. Read base config
            kv_source = os.path.join(
                self.base_theme_dir, f"{self.base_theme_name}.kvconfig"
            )
            with open(kv_source, "r", encoding="utf-8") as f:
                kvconfig_content = f.read()

            # 3. Modify colors
            # We need to replace the [GeneralColors] section or append to it if we want to override.
            # Easiest way is to append overrides to the end of the file, as Kvantum reads ini files
            # and later keys override earlier ones, BUT for [GeneralColors], we should replace the block.

            # Simple approach: just write a fresh file based on the template
            # For robustness, we will parse the lines and replace them
            new_lines = []
            in_colors = False

            primary = palette.get("primary", "#3f67a5")
            surface = palette.get("surface", "#2E2E2E")
            background = palette.get("background", "#2E2E2E")
            on_surface = palette.get(
                "on_background", "#FFFFFF"
            )  # Dynamically adapt to light/dark and enforce contrast
            on_primary = palette.get("on_primary", "#000000")
            error = palette.get("error", "#FF6666")

            color_overrides = {
                "window.color": background,
                "base.color": surface,
                "alt.base.color": surface,
                "button.color": palette.get(
                    "surface_variant", "#444444"
                ),  # Use proper variant
                "highlight.color": primary,
                "text.color": on_surface,
                "window.text.color": on_surface,
                "button.text.color": on_surface,
                "tooltip.text.color": on_surface,
                "highlight.text.color": on_primary,
                "link.color": primary,
                "link.visited.color": error,
            }

            with open(kv_source, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("[GeneralColors]"):
                        in_colors = True
                        new_lines.append(line)
                        for k, v in color_overrides.items():
                            new_lines.append(f"{k}={v}\n")
                        continue
                    elif line.startswith("[") and in_colors:
                        in_colors = False

                    if not in_colors:
                        # Also replace occurrences of base theme name if needed
                        # Kvantum internal names might be an issue, though usually just the file name matters
                        new_lines.append(
                            line.replace(self.base_theme_name, self.target_theme_name)
                        )

            target_kvconfig = os.path.join(
                self.target_dir, f"{self.target_theme_name}.kvconfig"
            )
            with open(target_kvconfig, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            logger.info(f"Generated Kvantum config at {target_kvconfig}")

            # 4. Apply using kvantummanager
            # We have to reload Kvantum configuration
            logger.info("Applying Kvantum theme via kvantummanager...")
            subprocess.run(
                ["kvantummanager", "--set", self.target_theme_name], check=True
            )
            logger.info("Kvantum theme applied successfully.")
            return True

        except Exception as e:
            logger.exception(f"Failed to generate Kvantum theme: {e}")
            return False


if __name__ == "__main__":
    kg = KvantumGenerator()
    palette_test = {
        "primary": "#ffaa00",
        "surface": "#1e1e1e",
        "background": "#111111",
        "error": "#ff0000",
    }
    kg.generate_and_apply(palette_test)
