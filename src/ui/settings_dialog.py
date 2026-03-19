import os
import platform
import subprocess
import configparser
from string import Template
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap

from config_manager import ConfigManager
from logger import logger


class SettingsDialog(QDialog):
    settings_saved = Signal()  # Signal emitted when settings are saved

    # --- Glass configuration per style ---
    _GLASS_PROFILES = {
        "Neon Glass":     {"alpha": 191, "frost_opacity": 0.06, "blur": True},
        "Frosted Glass":  {"alpha": 153, "frost_opacity": 0.12, "blur": True},
        "Material Pure":  {"alpha": 255, "frost_opacity": 0.0,  "blur": False},
    }
    _BASE_RGB = (15, 17, 26)  # Dark background base

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager

        self.setWindowTitle("Beauty Engine Settings")

        # Load custom app icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(600, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Always keep translucent — we control opacity via paintEvent
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Animated opacity property (0–255)
        self._bg_alpha = 255
        self._bg_color = QColor(*self._BASE_RGB, 255)

        # Frost overlay
        self._frost_pixmap = self._load_frost_texture()
        self._frost_opacity = 0.0

        # Animation objects (created once, reused)
        self._alpha_anim = QPropertyAnimation(self, b"bgAlpha", self)
        self._alpha_anim.setDuration(300)
        self._alpha_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self._frost_anim = QPropertyAnimation(self, b"frostOpacity", self)
        self._frost_anim.setDuration(300)
        self._frost_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.setup_ui()
        self.load_current_settings()

    # --- Qt Properties for animation ---
    def _get_bg_alpha(self) -> int:
        return self._bg_alpha

    def _set_bg_alpha(self, value: int):
        self._bg_alpha = value
        r, g, b = self._BASE_RGB
        self._bg_color = QColor(r, g, b, value)
        self.update()  # trigger repaint

    bgAlpha = Property(int, _get_bg_alpha, _set_bg_alpha)

    def _get_frost_opacity(self) -> float:
        return self._frost_opacity

    def _set_frost_opacity(self, value: float):
        self._frost_opacity = value
        self.update()  # trigger repaint

    frostOpacity = Property(float, _get_frost_opacity, _set_frost_opacity)

    # --- Texture loading ---
    def _load_frost_texture(self) -> QPixmap:
        """Load the tileable frost noise texture."""
        tex_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "textures", "frost_noise.png"
        )
        if os.path.exists(tex_path):
            return QPixmap(tex_path)
        logger.warning(f"Frost texture not found at {tex_path}")
        return QPixmap()

    # --- KWin Blur helper ---
    def _set_kwin_blur(self, enabled: bool):
        """Toggle KWin blur-behind via xprop (works under xcb / XWayland)."""
        if platform.system() != "Linux":
            return
        try:
            wid = str(int(self.winId()))
            if enabled:
                subprocess.run(
                    ["xprop", "-f", "_KDE_NET_WM_BLUR_BEHIND_REGION", "32c",
                     "-set", "_KDE_NET_WM_BLUR_BEHIND_REGION", "0", "-id", wid],
                    capture_output=True,
                )
            else:
                subprocess.run(
                    ["xprop", "-remove", "_KDE_NET_WM_BLUR_BEHIND_REGION", "-id", wid],
                    capture_output=True,
                )
        except Exception as e:
            logger.warning(f"Could not set window blur property: {e}")

    # --- Paint ---
    def paintEvent(self, event):
        """Paint semi-transparent bg + tileable frost noise overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1) Draw rounded semi-transparent background
        painter.setBrush(self._bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

        # 2) Draw frost noise overlay (tiled) with current opacity
        if self._frost_opacity > 0.01 and not self._frost_pixmap.isNull():
            painter.setOpacity(self._frost_opacity)
            pw, ph = self._frost_pixmap.width(), self._frost_pixmap.height()
            for x in range(0, self.width(), pw):
                for y in range(0, self.height(), ph):
                    painter.drawPixmap(x, y, self._frost_pixmap)
            painter.setOpacity(1.0)

        painter.end()
        super().paintEvent(event)

    def showEvent(self, event):
        """Re-apply blur properties every time the dialog becomes visible."""
        super().showEvent(event)
        self.update_stylesheet()

    def update_stylesheet(self):
        chevron_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", "chevron-down.svg"))
        chevron_path = chevron_path.replace("\\", "/")

        try:
            current_style = self.profile_combo.currentText()
        except AttributeError:
            current_style = ""

        # Resolve glass profile for this style
        profile = self._GLASS_PROFILES.get(current_style, self._GLASS_PROFILES["Material Pure"])
        target_alpha = profile["alpha"]
        target_frost = profile["frost_opacity"]

        # Animate background opacity
        self._alpha_anim.stop()
        self._alpha_anim.setStartValue(self._bg_alpha)
        self._alpha_anim.setEndValue(target_alpha)
        self._alpha_anim.start()

        # Animate frost overlay opacity
        self._frost_anim.stop()
        self._frost_anim.setStartValue(self._frost_opacity)
        self._frost_anim.setEndValue(target_frost)
        self._frost_anim.start()

        # Toggle KWin blur
        self._set_kwin_blur(profile["blur"])

        # Define default dynamic colors mapped from the QSS layout
        colors = {
            "text_primary": "#ffffff",
            "text_secondary": "#a9b1d6",
            "text_muted": "#565f89",
            "text_button": "#ffffff",
            "card_bg": "rgba(255, 255, 255, 0.04)",
            "card_border": "rgba(255, 255, 255, 0.08)",
            "indicator_bg": "rgba(0, 0, 0, 0.3)",
            "indicator_border": "rgba(255, 255, 255, 0.1)",
            "indicator_hover": "rgba(0, 0, 0, 0.4)",
            "accent_color": "#2f64ff",
            "accent_hover": "#4371ff",
            "accent_pressed": "#1c48cc",
            "combo_bg": "rgba(0, 0, 0, 0.2)",
            "combo_border": "rgba(255, 255, 255, 0.1)",
            "combo_hover_bg": "rgba(0, 0, 0, 0.3)",
            "menu_bg": "rgba(20, 22, 33, 0.95)",
            "menu_border": "rgba(255, 255, 255, 0.1)",
            "menu_item_hover": "rgba(47, 100, 255, 0.2)",
            "cancel_bg": "rgba(255, 255, 255, 0.08)",
            "cancel_hover": "rgba(255, 255, 255, 0.12)",
            "chevron_path": chevron_path,
        }

        # Try mapping KDE colors from the AdaptiveCachy palette file generated by the engine
        colors_conf = os.path.expanduser("~/.local/share/color-schemes/AdaptiveCachy.colors")
        if os.path.exists(colors_conf):
            parser = configparser.ConfigParser()
            parser.read(colors_conf)
            if "Colors:Selection" in parser and "BackgroundNormal" in parser["Colors:Selection"]:
                rgb = parser["Colors:Selection"]["BackgroundNormal"].split(",")
                if len(rgb) == 3:
                     # Dynamically bind system accent to settings menu buttons and focus rings
                     hex_accent = f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
                     colors["accent_color"] = hex_accent
                     # Map hovering overlay for items
                     colors["menu_item_hover"] = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"
            if "Colors:Window" in parser and "ForegroundNormal" in parser["Colors:Window"]:
                rgb_text = parser["Colors:Window"]["ForegroundNormal"].split(",")
                if len(rgb_text) == 3:
                     hex_text = f"#{int(rgb_text[0]):02x}{int(rgb_text[1]):02x}{int(rgb_text[2]):02x}"
                     colors["text_primary"] = hex_text

        # Load extracted QSS templates
        qss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "styles", "settings_dialog.qss"))
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
            self.setStyleSheet(Template(stylesheet).safe_substitute(colors))
        else:
            logger.warning(f"Extracted QSS not found at {qss_path}. Reverting to no style.")

    def _on_profile_changed(self, text):
        self.update_stylesheet()

    def setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(40, 40, 40, 40)
        self._main_layout.setSpacing(20)

        self._build_header()
        self._build_main_card()
        self._build_toggles_card()

        self._main_layout.addStretch()

        self._build_actions()
        self._apply_popup_transparency()

    def _build_header(self):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)

        title = QLabel("Preferences")
        title.setObjectName("Title")
        header_layout.addWidget(title)

        subtitle = QLabel("Configure your Adaptive Cachy Beauty Core")
        subtitle.setObjectName("Subtitle")
        header_layout.addWidget(subtitle)

        self._main_layout.addLayout(header_layout)

    def _build_main_card(self):
        main_card = QFrame()
        main_card.setObjectName("Card")
        grid = QGridLayout(main_card)
        grid.setVerticalSpacing(24)
        grid.setHorizontalSpacing(32)
        grid.setContentsMargins(28, 28, 28, 28)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        main_card.setGraphicsEffect(shadow)

        # Mode Selection
        mode_label = QLabel("Theme Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Dark", "Light"])
        self.mode_combo.setFixedHeight(38)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(mode_label, 0, 0)
        grid.addWidget(self.mode_combo, 0, 1)

        # Contrast Level
        contrast_label = QLabel("Contrast Level:")
        self.contrast_combo = QComboBox()
        self.contrast_combo.addItems(["Standard", "High", "Medium"])
        self.contrast_combo.setFixedHeight(38)
        self.contrast_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(contrast_label, 1, 0)
        grid.addWidget(self.contrast_combo, 1, 1)

        # Theme Style
        profile_label = QLabel("Theme Style:")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(
            [
                "Neon Glass",
                "Frosted Glass",
                "Material Pure",
            ]
        )
        self.profile_combo.setFixedHeight(38)
        self.profile_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        grid.addWidget(profile_label, 2, 0)
        grid.addWidget(self.profile_combo, 2, 1)

        grid.setRowStretch(3, 1)
        self._main_layout.addWidget(main_card)

    def _build_toggles_card(self):
        toggles_card = QFrame()
        toggles_card.setObjectName("Card")
        toggles_layout = QVBoxLayout(toggles_card)
        toggles_layout.setSpacing(20)
        toggles_layout.setContentsMargins(24, 24, 24, 24)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        toggles_card.setGraphicsEffect(shadow)

        self.kvantum_check = QCheckBox("Enable Kvantum Window Theming")
        self.kvantum_check.setMinimumHeight(38)
        toggles_layout.addWidget(self.kvantum_check)

        self.konsole_check = QCheckBox("Enable Konsole Profile Generation")
        self.konsole_check.setMinimumHeight(38)
        toggles_layout.addWidget(self.konsole_check)

        self._main_layout.addWidget(toggles_card)

    def _build_actions(self):
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save && Apply")
        self.save_btn.clicked.connect(self.save_settings)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        self._main_layout.addLayout(btn_layout)

    def _apply_popup_transparency(self):
        for combo in (self.mode_combo, self.contrast_combo, self.profile_combo):
            container = combo.view().parentWidget()
            if container:
                container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
                container.setAttribute(Qt.WA_TranslucentBackground)
                container.setObjectName("ComboContainer")
                container.setStyleSheet("#ComboContainer { background: transparent; border: none; }")

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
