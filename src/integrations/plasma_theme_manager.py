import os
import subprocess
import configparser

from logger import logger


class PlasmaThemeManager:
    def __init__(self):
        self.colors_dir = os.path.expanduser("~/.local/share/color-schemes")
        os.makedirs(self.colors_dir, exist_ok=True)

    def rgb_from_hex(self, hex_color: str) -> str:
        """Convert #RRGGBB to R,G,B string for KDE colors scheme."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r},{g},{b}"

    def generate_and_apply_theme(
        self, palette: dict, theme_name: str = "AdaptiveBeauty"
    ):
        """Generates a .colors file and applies it using plasma-apply-colorscheme."""
        file_path = os.path.join(self.colors_dir, f"{theme_name}.colors")

        # We need a base template, but for now we write a minimal KDE Color Scheme
        # KDE 6 usually requires some specific sections. We will construct a minimal one.
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case

        # KDE Color Scheme Format
        config["General"] = {"ColorScheme": theme_name, "Name": theme_name}

        # Material You to KDE mapping logic
        bg = self.rgb_from_hex(palette["background"])
        fg = self.rgb_from_hex(
            palette.get("on_background", palette["on_primary_container"])
        )  # Protected contrast text
        fg_inactive = self.rgb_from_hex(
            palette.get("color8", palette["secondary"])
        )  # Dimmer but readable text

        primary = self.rgb_from_hex(palette["primary"])
        on_primary = self.rgb_from_hex(palette["on_primary"])

        primary_container = self.rgb_from_hex(palette["primary_container"])
        on_primary_container = self.rgb_from_hex(palette["on_primary_container"])

        surface = self.rgb_from_hex(palette["surface"])
        surface_variant = self.rgb_from_hex(
            palette.get("surface_variant", palette["background"])
        )

        error = self.rgb_from_hex(palette["error"])

        # Colors: Window
        config["Colors:Window"] = {
            "BackgroundNormal": bg,
            "BackgroundAlternate": surface_variant,
            "ForegroundNormal": fg,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        # Colors: View
        config["Colors:View"] = {
            "BackgroundNormal": surface,
            "BackgroundAlternate": surface_variant,
            "ForegroundNormal": fg,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        # Colors: Button
        config["Colors:Button"] = {
            "BackgroundNormal": surface_variant,
            "BackgroundAlternate": surface_variant,
            "ForegroundNormal": fg,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        # Colors: Selection
        config["Colors:Selection"] = {
            "BackgroundNormal": primary,
            "BackgroundAlternate": primary,
            "ForegroundNormal": on_primary,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        # Colors: Tooltip
        config["Colors:Tooltip"] = {
            "BackgroundNormal": surface_variant,
            "BackgroundAlternate": surface_variant,
            "ForegroundNormal": fg,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        # Colors: Complementary (Often used for plasma panels)
        config["Colors:Complementary"] = {
            "BackgroundNormal": primary_container,
            "BackgroundAlternate": surface_variant,
            "ForegroundNormal": on_primary_container,
            "ForegroundInactive": fg_inactive,
            "DecorationFocus": primary,
            "DecorationHover": primary,
        }

        config["WM"] = {
            "activeBackground": primary_container,
            "activeBlend": primary_container,
            "activeForeground": on_primary_container,
            "inactiveBackground": surface,
            "inactiveBlend": surface,
            "inactiveForeground": fg_inactive,
        }

        with open(file_path, "w") as f:
            config.write(f)

        logger.debug(f"Theme file written to {file_path}")

        # Apply the theme
        # Workaround: Plasma won't reload the theme if the name is the same as the currently active one.
        # We briefly switch to 'BreezeLight' or 'BreezeDark' to force a reload.
        try:
            logger.debug("Applying BreezeDark as a workaround to clear cache...")
            subprocess.run(
                ["plasma-apply-colorscheme", "BreezeDark"],
                check=True,
                capture_output=True,
            )

            logger.debug(f"Applying final theme: {theme_name}...")
            subprocess.run(
                ["plasma-apply-colorscheme", theme_name],
                check=True,
                capture_output=True,
            )

            logger.info(f"Successfully applied KDE Plasma theme: {theme_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply theme to Plasma: {e.stderr}")

    def generate_konsole_theme(self, palette: dict, theme_name: str = "AdaptiveCachy"):
        """Generates a Konsole .colorscheme file."""
        konsole_dir = os.path.expanduser("~/.local/share/konsole")
        os.makedirs(konsole_dir, exist_ok=True)
        file_path = os.path.join(konsole_dir, f"{theme_name}.colorscheme")

        config = configparser.ConfigParser()
        config.optionxform = str

        bg = self.rgb_from_hex(palette["background"])
        fg = self.rgb_from_hex(
            palette.get("on_background", palette["on_primary_container"])
        )
        primary = self.rgb_from_hex(palette["primary"])

        config["Background"] = {"Color": bg, "Transparency": "False"}
        config["BackgroundIntense"] = {"Color": bg, "Transparency": "False"}
        config["Foreground"] = {"Color": fg, "Transparency": "False"}
        config["ForegroundIntense"] = {"Color": primary, "Transparency": "False"}

        config["General"] = {"Description": theme_name, "Opacity": "1"}

        # Simple colors
        config["Color0"] = {"Color": bg}
        config["Color1"] = {"Color": self.rgb_from_hex(palette.get("error", "#ff0000"))}
        config["Color2"] = {
            "Color": self.rgb_from_hex(palette.get("secondary", "#00ff00"))
        }
        config["Color3"] = {"Color": primary}
        config["Color4"] = {
            "Color": self.rgb_from_hex(palette.get("tertiary", "#0000ff"))
        }
        config["Color5"] = {"Color": primary}
        config["Color6"] = {"Color": primary}
        config["Color7"] = {"Color": fg}

        with open(file_path, "w") as f:
            config.write(f)

        logger.info(f"Generated Konsole theme: {file_path}")


if __name__ == "__main__":
    # Test
    manager = PlasmaThemeManager()
    test_palette = {
        "primary": "#f9b6ac",
        "on_primary": "#61332d",
        "primary_container": "#76453e",
        "on_primary_container": "#ffdbd6",
        "secondary": "#e7bdb6",
        "background": "#130d0b",
        "surface": "#130d0b",
        "error": "#f97386",
    }
    manager.generate_and_apply_theme(test_palette)
