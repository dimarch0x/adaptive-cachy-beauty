import os
from colorthief import ColorThief
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.hct import Hct
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from PIL import Image

from logger import logger


class ThemeGenerator:
    def __init__(self):
        pass

    def extract_colorthief_palette(self, image_path: str, color_count: int = 5) -> dict:
        """Extracts basic dominant color and palette using ColorThief."""
        if not os.path.exists(image_path):
            logger.error(f"Image not found at {image_path}")
            raise FileNotFoundError(f"Image not found at {image_path}")

        logger.debug(f"ColorThief extraction for {image_path}")
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=1)
        palette = color_thief.get_palette(color_count=color_count, quality=1)
        return {"dominant": dominant_color, "palette": palette}

    def _rgb_to_int(self, r, g, b):
        return (255 << 24) | (r << 16) | (g << 8) | b

    def _int_to_hex(self, i):
        return f"#{i & 0xFFFFFF:06x}"

    def _ensure_contrast_hct(
        self, color_argb: int, bg_argb: int, min_delta: float = 50.0
    ) -> int:
        """Ensures color has at least min_delta Tone difference from bg. Returns updated ARGB."""
        color_hct = Hct.from_int(color_argb)
        bg_hct = Hct.from_int(bg_argb)

        tone_delta = abs(bg_hct.tone - color_hct.tone)
        if tone_delta < min_delta:
            if bg_hct.tone < 50:  # Dark background, lighten the color
                color_hct.tone = min(100.0, bg_hct.tone + min_delta)
            else:  # Light background, darken the color
                color_hct.tone = max(0.0, bg_hct.tone - min_delta)
        return color_hct.to_int()

    def _generate_ansi_colors(
        self, base_hct: Hct, is_dark: bool, bg_argb: int, style: str
    ) -> dict:
        """Generates standard 16 terminal colors obeying style semantics but forcing distinct hues."""
        # Define expected baseline ANSI hues
        hues = {
            "red": 10.0,
            "green": 130.0,
            "yellow": 60.0,
            "blue": 250.0,
            "magenta": 300.0,
            "cyan": 190.0,
        }

        # Determine chroma based on generation style
        style = style.strip().lower()
        if style == "neon glass":
            base_chroma = max(base_hct.chroma, 48.0)  # Very vibrant
        elif style == "vivid high-contrast":
            base_chroma = max(base_hct.chroma, 40.0)  # Expressive
        elif style == "frosted glass" or style == "material pure":
            base_chroma = max(base_hct.chroma, 24.0)  # Standard Tonal
        else:  # soft muted
            base_chroma = min(max(base_hct.chroma, 8.0), 16.0)  # Desaturated

        bg_tone = Hct.from_int(bg_argb).tone

        # Terminal Tone configurations
        normal_tone = 70.0 if bg_tone < 50 else 30.0
        bright_tone = 80.0 if bg_tone < 50 else 20.0

        # Color0/Color8 (Black/Gray semantics)
        color0 = Hct.from_hct(
            base_hct.hue, min(base_chroma, 10.0), 30.0 if bg_tone < 50 else 90.0
        ).to_int()
        color8 = Hct.from_hct(
            base_hct.hue, min(base_chroma, 10.0), 50.0 if bg_tone < 50 else 70.0
        ).to_int()

        # Color7/Color15 (White/Foreground semantics)
        color7 = Hct.from_hct(
            base_hct.hue, min(base_chroma, 8.0), 85.0 if bg_tone < 50 else 15.0
        ).to_int()
        color15 = Hct.from_hct(
            base_hct.hue, min(base_chroma, 8.0), 95.0 if bg_tone < 50 else 10.0
        ).to_int()

        # Build map and contrast-protect every color
        ansi = {
            "color0": self._int_to_hex(
                self._ensure_contrast_hct(color0, bg_argb, 10.0)
            ),  # Low contrast ok for hidden text
            "color1": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["red"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color2": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["green"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color3": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["yellow"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color4": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["blue"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color5": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["magenta"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color6": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["cyan"], base_chroma, normal_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color7": self._int_to_hex(
                self._ensure_contrast_hct(color7, bg_argb, 50.0)
            ),
            "color8": self._int_to_hex(
                self._ensure_contrast_hct(color8, bg_argb, 20.0)
            ),
            "color9": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["red"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color10": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["green"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color11": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["yellow"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color12": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["blue"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color13": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["magenta"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color14": self._int_to_hex(
                self._ensure_contrast_hct(
                    Hct.from_hct(hues["cyan"], base_chroma, bright_tone).to_int(),
                    bg_argb,
                    40.0,
                )
            ),
            "color15": self._int_to_hex(
                self._ensure_contrast_hct(color15, bg_argb, 60.0)
            ),  # Max contrast text
        }
        return ansi

    def generate_material_you_palette(
        self, image_path: str, is_dark: bool = True, style: str = "Neon Glass", contrast_level: str = "medium"
    ) -> dict:
        """Generates a complete Material You palette from an image using the specified Style and ensures readability."""
        if not os.path.exists(image_path):
            logger.error(f"Image not found at {image_path}")
            raise FileNotFoundError(f"Image not found at {image_path}")

        logger.debug(f"Generating Material You {style} palette for {image_path}")

        # Open image and resize for performance
        img = Image.open(image_path)
        img.thumbnail((128, 128))

        # Convert to RGB to ensure we get (R, G, B) tuples, not palettes or flat ints
        img = img.convert("RGB")

        # Extract pixels
        pixels = (
            list(img.getdata())
            if not hasattr(img, "get_flattened_data")
            else list(img.get_flattened_data())
        )

        # QuantizeCelebi expects sequences of [R, G, B, A]
        pixels_rgba = [[p[0], p[1], p[2], 255] for p in pixels]

        # Use Celebi quantization expectation: list of [a, r, g, b]
        quantization_result = QuantizeCelebi(pixels_rgba, 128)

        # Detect if the image is essentially monochrome to prevent Score.score() Google Blue fallback
        max_chroma = 0.0
        for argb in quantization_result.keys():
            chroma = Hct.from_int(argb).chroma
            if chroma > max_chroma:
                max_chroma = chroma

        is_monochrome = max_chroma < 15.0

        if is_monochrome:
            logger.info(f"Monochrome image detected (max chroma {max_chroma:.1f}). Overriding fallback scoring.")
            # Fallback to the most frequent actual color instead of Google Blue
            if quantization_result:
                dominant_argb = max(quantization_result.items(), key=lambda item: item[1])[0]
            else:
                dominant_argb = 0xFF888888  # Safe neutral gray
            
            # Force exactly 0 chroma to keep the outcome cleanly gray (prevents "muddy" tints)
            hct = Hct.from_int(dominant_argb)
            hct.chroma = 0.0
            dominant_argb = hct.to_int()
            
            # Critical: SchemeVibrant (Neon Glass) forces chroma to 48 even if input is 0.
            # For a truly grayscale image, we MUST enforce SchemeMonochrome to prevent hue hallucination.
            style = "soft muted"
        else:
            # Get dominant color based on standard scoring
            dominant_argb = Score.score(quantization_result)[0]

        # Build Scheme based on generation style
        hct_color = Hct.from_int(dominant_argb)

        style = style.strip().lower()
        if style == "neon glass":
            scheme = SchemeVibrant(hct_color, is_dark, 0.0)
        elif style == "frosted glass":
            scheme = SchemeNeutral(hct_color, is_dark, 0.0)
        elif style == "vivid high-contrast":
            scheme = SchemeExpressive(hct_color, is_dark, 0.0)
        elif style == "soft muted":
            scheme = SchemeMonochrome(hct_color, is_dark, 0.0)
        else:
            # Fallback and Material Pure default
            scheme = SchemeTonalSpot(hct_color, is_dark, 0.0)

        # Background extraction
        bg_argb = MaterialDynamicColors.background.get_argb(scheme)

        # Smart Contrast Engine (Readability Fix V2)
        # Determine base thresholds based on user selected Contrast Level
        contrast_level = contrast_level.strip().lower()
        if contrast_level == "high":
            base_delta = 65.0
            text_delta = 75.0
        elif contrast_level == "medium" or contrast_level == "standard":
            base_delta = 50.0
            text_delta = 60.0
        else: # low / minimal (though standard is default)
            base_delta = 40.0
            text_delta = 50.0

        # Apply strict WCAG contrast guards to the baseline text elements
        primary_argb = self._ensure_contrast_hct(
            MaterialDynamicColors.primary.get_argb(scheme), bg_argb, base_delta
        )
        on_background_argb = self._ensure_contrast_hct(
            MaterialDynamicColors.onBackground.get_argb(scheme), bg_argb, text_delta
        )  # Main UI text must be perfectly readable

        # Protected Container Contrast (Dolphin pathbars, Window headers)
        pc_argb = MaterialDynamicColors.primaryContainer.get_argb(scheme)
        opc_argb = MaterialDynamicColors.onPrimaryContainer.get_argb(scheme)

        if style == "neon glass" and is_dark:
            # For Neon Glass, we want deep dark headers with vibrant neon text
            pc_hct = Hct.from_int(pc_argb)
            pc_hct.tone = 10.0  # Force very dark background for titlebars
            pc_argb = pc_hct.to_int()
            
            opc_hct = Hct.from_int(opc_argb)
            opc_hct.tone = 90.0  # Force very light/neon text
            opc_argb = opc_hct.to_int()
        else:
            # Standard contrast protection for other styles using user's contrast level
            opc_argb = self._ensure_contrast_hct(opc_argb, pc_argb, base_delta)

        # Extract useful UI colors
        palette = {
            "primary": self._int_to_hex(primary_argb),
            "on_primary": self._int_to_hex(
                MaterialDynamicColors.onPrimary.get_argb(scheme)
            ),
            "primary_container": self._int_to_hex(pc_argb),
            "on_primary_container": self._int_to_hex(opc_argb),
            "secondary": self._int_to_hex(
                MaterialDynamicColors.secondary.get_argb(scheme)
            ),
            "background": self._int_to_hex(bg_argb),
            "on_background": self._int_to_hex(on_background_argb),
            "surface": self._int_to_hex(MaterialDynamicColors.surface.get_argb(scheme)),
            "surface_variant": self._int_to_hex(
                MaterialDynamicColors.surfaceVariant.get_argb(scheme)
            ),
            "error": self._int_to_hex(MaterialDynamicColors.error.get_argb(scheme)),
        }

        # Inject ANSI explicitly calculated colors
        ansi_colors = self._generate_ansi_colors(hct_color, is_dark, bg_argb, style)
        palette.update(ansi_colors)

        return palette


if __name__ == "__main__":
    generator = ThemeGenerator()
    import sys

    # Try logic by default using a fallback or provided argument
    test_image = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/usr/share/wallpapers/cachyos-wallpapers/df0ae2f5-41d9-421e-8e63-c098ad1ff49a_изображение.png"
    )

    if os.path.exists(test_image):
        print(f"Analyzing {test_image}...")

        print("\n--- ColorThief Extraction ---")
        basic = generator.extract_colors_colorthief(test_image)
        print(basic)

        print("\n--- Material You Generation ---")
        my_dark = generator.generate_material_you_palette(test_image, is_dark=True)
        print("Dark Mode Palette:", my_dark)
    else:
        print(f"Skipping test, image {test_image} not found.")
