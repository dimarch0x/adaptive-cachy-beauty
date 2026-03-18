import sys
import os
import unittest
from materialyoucolor.hct import Hct

# Add src to path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_project_root, "src"))
from core.theme_generator import ThemeGenerator


class TestSmartContrastPairs(unittest.TestCase):
    def setUp(self):
        self.generator = ThemeGenerator()
        # Use a high contrast testing scenario that naturally breaks Material You's tonal assumptions
        # E.g. Soft Muted puts everything close to 50-60 tone, destroying contrast between pairs
        self.test_image = (
            "/usr/share/wallpapers/cachyos-wallpapers/wallhaven-yqe81l.png"
        )

    def _get_delta_t(self, hex1, hex2):
        # Convert #RRGGBB to ARGB
        rgb1 = int(hex1.lstrip("#"), 16) | 0xFF000000
        rgb2 = int(hex2.lstrip("#"), 16) | 0xFF000000
        t1 = Hct.from_int(rgb1).tone
        t2 = Hct.from_int(rgb2).tone
        return abs(t1 - t2)

    def test_container_contrast_muted(self):
        """Test if Container backgrounds have readable text in Soft Muted style."""
        if not os.path.exists(self.test_image):
            self.skipTest("Test image not found")

        palette = self.generator.generate_material_you_palette(
            self.test_image, is_dark=True, style="Soft Muted"
        )

        # In KDE Plasma, Dolphin Path / Active windows use primary_container / bg_alt and on_primary_container!
        container_bg = palette["primary_container"]
        container_fg = palette["on_primary_container"]

        delta = self._get_delta_t(container_bg, container_fg)

        print(
            f"\n[Soft Muted] Container BG: {container_bg}, Text: {container_fg} -> Delta T = {delta:.1f}"
        )

        # Test should fail because Delta T in Soft Muted is usually small (< 40) for these pairs
        self.assertGreaterEqual(
            delta,
            50.0,
            "Contrast between Container BG and Text is too low for readability!",
        )

    def test_primary_contrast_vivid(self):
        """Test if Primary buttons have readable text in Vivid style."""
        if not os.path.exists(self.test_image):
            self.skipTest("Test image not found")

        palette = self.generator.generate_material_you_palette(
            self.test_image, is_dark=True, style="Vivid High-Contrast"
        )

        primary_bg = palette["primary"]
        primary_fg = palette["on_primary"]

        delta = self._get_delta_t(primary_bg, primary_fg)

        print(
            f"\n[Vivid] Primary BG: {primary_bg}, Text: {primary_fg} -> Delta T = {delta:.1f}"
        )

        self.assertGreaterEqual(
            delta,
            50.0,
            "Contrast between Primary BG and Text is too low for readability!",
        )


if __name__ == "__main__":
    unittest.main()
