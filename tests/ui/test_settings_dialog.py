import sys
import os
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure src is in path so we can import internal modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from ui.settings_dialog import SettingsDialog
from config_manager import ConfigManager

@pytest.fixture
def config_manager(tmp_path):
    """Fixture to provide an isolated and safe config manager"""
    cm = ConfigManager()
    # Override path to temporary directory for tests
    cm.config_dir = str(tmp_path)
    cm.config_path = os.path.join(cm.config_dir, "config.json")
    cm.settings = {
        "dark_mode": True,
        "enable_kvantum": True,
        "enable_konsole": True,
        "contrast_level": "normal",
        "theme_style": "Neon Glass",
    }
    return cm

def test_settings_dialog_initialization(qtbot, config_manager):
    """Test that SettingsDialog initializes properly, config loads correctly"""
    dialog = SettingsDialog(config_manager)
    qtbot.addWidget(dialog)

    # Validate combobox pre-loads configuration
    assert dialog.profile_combo.currentText() == "Neon Glass"
    assert dialog.kvantum_check.isChecked() is True

def test_settings_dialog_save_logic(qtbot, config_manager, mocker):
    """Test that UI changes save their state back via config manager"""
    dialog = SettingsDialog(config_manager)
    qtbot.addWidget(dialog)

    # Simulate UI modifications
    dialog.profile_combo.setCurrentText("Frosted Glass")
    dialog.kvantum_check.setChecked(False)

    # Trigger save button click inside a signal catcher
    with qtbot.waitSignal(dialog.settings_saved, timeout=1000):
        qtbot.mouseClick(dialog.save_btn, Qt.MouseButton.LeftButton)

    # Verify ConfigManager got the signals
    assert config_manager.get("theme_style") == "Frosted Glass"
    assert config_manager.get("enable_kvantum") is False
