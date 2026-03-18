import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFrame,
    QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from config_manager import ConfigManager
from logger import logger


class SettingsDialog(QDialog):
    settings_saved = Signal()  # Signal emitted when settings are saved

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager

        self.setWindowTitle("Beauty Engine Settings")
        
        # Load custom app icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setFixedSize(550, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setup_ui()
        self.load_current_settings()

    def update_stylesheet(self):
        try:
            current_style = self.profile_combo.currentText()
        except AttributeError:
            current_style = ""

        is_glass = "Glass" in current_style

        # Toggle translucent background dynamically
        self.setAttribute(Qt.WA_TranslucentBackground, is_glass)
        bg_color = "rgba(15, 17, 26, 0.65)" if is_glass else "#0f111a"

        # Dynamically apply/remove KWin Blur using xprop (Works because of QT_QPA_PLATFORM=xcb)
        import platform
        import subprocess
        if platform.system() == 'Linux':
            wid = str(int(self.winId()))
            try:
                if is_glass:
                    subprocess.run(['xprop', '-f', '_KDE_NET_WM_BLUR_BEHIND_REGION', '32c', '-set', '_KDE_NET_WM_BLUR_BEHIND_REGION', '0', '-id', wid], capture_output=True)
                else:
                    subprocess.run(['xprop', '-remove', '_KDE_NET_WM_BLUR_BEHIND_REGION', '-id', wid], capture_output=True)
            except Exception as e:
                logger.warning(f"Could not set window blur property: {e}")

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                font-family: 'Inter', 'Roboto', sans-serif;
            }}
            QLabel {{
                font-size: 14px;
                color: #a9b1d6;
                font-weight: 500;
            }}
            QLabel#Title {{
                font-size: 24px;
                font-weight: 800;
                color: #7aa2f7;
                min-height: 36px;
                padding-bottom: 5px;
            }}
            QLabel#Subtitle {{
                font-size: 13px;
                color: #565f89;
                margin-bottom: 20px;
            }}
            QCheckBox {{
                font-size: 14px;
                color: #c0caf5;
                spacing: 12px;
                padding: 5px 0px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #414868;
                background-color: #1a1b26;
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid #7aa2f7;
            }}
            QCheckBox::indicator:checked {{
                background-color: #7aa2f7;
                border: 2px solid #7aa2f7;
            }}
            QComboBox {{
                background-color: #1a1b26;
                border: 2px solid #24283b;
                border-radius: 8px;
                padding: 6px 15px;
                color: #c0caf5;
                font-size: 13px;
                font-weight: 600;
                min-width: 150px;
                min-height: 34px;
            }}
            QComboBox:hover {{
                border: 2px solid #414868;
            }}
            QComboBox:focus {{
                border: 2px solid #7aa2f7;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QFrame#Separator {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(122, 162, 247, 0), stop:0.5 rgba(122, 162, 247, 150), stop:1 rgba(122, 162, 247, 0));
                max-height: 1px;
                margin: 20px 0px;
            }}
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7aa2f7, stop:1 #bb9af7);
                color: #15161e;
                border-radius: 8px;
                padding: 6px 20px;
                font-weight: 800;
                font-size: 14px;
                border: none;
                min-height: 38px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8db0fc, stop:1 #cbb1fc);
            }}
            QPushButton:pressed {{
                background-color: #7aa2f7;
            }}
            QPushButton#CancelBtn {{
                background-color: #1a1b26;
                border: 2px solid #24283b;
                color: #a9b1d6;
                min-height: 34px;
            }}
            QPushButton#CancelBtn:hover {{
                border: 2px solid #414868;
                color: #c0caf5;
            }}
        """)

    def _on_profile_changed(self, text):
        self.update_stylesheet()

    def setup_ui(self):
        # Modern Premium Styling - Glassmorphism & Neon accents
        # Stylesheet is now managed dynamically by update_stylesheet
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        # Header Section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        
        title = QLabel("Preferences")
        title.setObjectName("Title")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Configure your Adaptive Cachy Beauty Core")
        subtitle.setObjectName("Subtitle")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Theme Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Dark", "Light"])
        mode_layout.addWidget(mode_label)
        mode_layout.addStretch()
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Contrast Level
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast Level:")
        self.contrast_combo = QComboBox()
        self.contrast_combo.addItems(["Standard", "High", "Medium"])
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addStretch()
        contrast_layout.addWidget(self.contrast_combo)
        layout.addLayout(contrast_layout)

        # Theme Style (Replaces Color Profile)
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Theme Style:")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(
            [
                "Neon Glass",
                "Frosted Glass",
                "Material Pure",
                "Vivid High-Contrast",
                "Soft Muted",
            ]
        )
        profile_layout.addWidget(profile_label)
        profile_layout.addStretch()
        profile_layout.addWidget(self.profile_combo)
        layout.addLayout(profile_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("Separator")
        layout.addWidget(line)

        # Toggles
        self.kvantum_check = QCheckBox("Enable Kvantum Window Theming")
        layout.addWidget(self.kvantum_check)

        self.konsole_check = QCheckBox("Enable Konsole Profile Generation")
        layout.addWidget(self.konsole_check)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.clicked.connect(self.save_settings)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)
        
        # Connect combo box to stylesheet updater for real-time blur feedback
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        
        # Initial stylesheet application
        self.update_stylesheet()

    def load_current_settings(self):
        is_dark = self.config.get("dark_mode", True)
        self.mode_combo.setCurrentText("Dark" if is_dark else "Light")

        # Contrast level mapping
        valid_contrast = ["Standard", "High", "Medium"]
        contrast = self.config.get("contrast_level", "Standard").capitalize()
        if contrast in valid_contrast:
            self.contrast_combo.setCurrentText(contrast)

        # Theme Style mapping
        valid_profiles = [
            "Neon Glass",
            "Frosted Glass",
            "Material Pure",
            "Vivid High-Contrast",
            "Soft Muted",
        ]
        profile = self.config.get("theme_style", "Neon Glass")
        # Ensure exact casing match if previously saved differently
        matched_profile = next(
            (p for p in valid_profiles if p.lower() == profile.lower()), "Neon Glass"
        )
        self.profile_combo.setCurrentText(matched_profile)

        self.kvantum_check.setChecked(bool(self.config.get("enable_kvantum", True)))
        self.konsole_check.setChecked(bool(self.config.get("enable_konsole", True)))

    def save_settings(self):
        is_dark = self.mode_combo.currentText() == "Dark"
        self.config.set("dark_mode", is_dark)

        self.config.set("contrast_level", self.contrast_combo.currentText().lower())
        self.config.set("theme_style", self.profile_combo.currentText())
        self.config.set("enable_kvantum", self.kvantum_check.isChecked())
        self.config.set("enable_konsole", self.konsole_check.isChecked())

        logger.info("User settings saved from Settings Dialog.")
        self.settings_saved.emit()
        self.accept()
