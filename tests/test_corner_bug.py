import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from PySide6.QtWidgets import QApplication
from ui.settings_dialog import SettingsDialog
from config_manager import ConfigManager

def test_kwin_blur_avoids_corner_bug():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    config = ConfigManager()
    dialog = SettingsDialog(config)
    
    with patch('subprocess.run') as mock_run:
        dialog._set_kwin_blur(True)
        # Check if subprocess.run was called with xprop
        mock_run.assert_called()
        args = mock_run.call_args[0][0]
        assert "xprop" in args
        # Ensure we pass "0" now because we use sharp corners to perfectly avoid the kornerbug.
        value_idx = args.index("-set") + 2
        value = args[value_idx]
        assert value == "0", "Blur region is not '0'"

if __name__ == "__main__":
    test_kwin_blur_avoids_corner_bug()
    print("Test passed!")
