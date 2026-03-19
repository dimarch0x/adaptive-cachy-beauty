import os
import platform
import subprocess
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
    QStyledItemDelegate,
)
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QUrl
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap, QDesktopServices

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
        self.current_palette = self.config.get("cached_palette", None)

        self.setWindowTitle("Beauty Engine Settings")

        # Load custom app icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(640, 680)
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

        try:
            is_dark = self.mode_combo.currentText() == "Dark"
        except AttributeError:
            # Fallback during early init before mode_combo exists
            is_dark = self.config.get("dark_mode", True)

        # Dynamically push background repaints to the root QDialog container
        self._BASE_RGB = (15, 17, 26) if is_dark else (245, 245, 250)
        if hasattr(self, "_bg_color"):
            self._bg_color.setRgb(*self._BASE_RGB, self._bg_alpha)
            self.update()

        p = self.current_palette or {}

        if is_dark:
            colors = {
                "text_primary": p.get("on_background", "#ffffff"),
                "text_secondary": p.get("on_surface_variant", "#a9b1d6"),
                "accent_color": p.get("primary", "#2f64ff"),
                "card_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(25, 27, 36, 0.8), stop:1 rgba(15, 17, 26, 0.9))",
                "card_border": "rgba(255, 255, 255, 0.08)",
                "checkbox_bg": "rgba(0, 0, 0, 0.3)",
                "checkbox_hover": "rgba(0, 0, 0, 0.4)",
                "checkbox_border": "rgba(255, 255, 255, 0.1)",
                "combo_bg": "rgba(0, 0, 0, 0.2)",
                "combo_hover_bg": "rgba(0, 0, 0, 0.3)",
                "combo_border": "rgba(255, 255, 255, 0.1)",
                "menu_bg": p.get("background", "rgba(20, 22, 33, 0.95)"),
                "menu_border": "rgba(255, 255, 255, 0.1)",
                "menu_item_hover": "rgba(255, 255, 255, 0.1)",
                "cancel_bg": "rgba(255, 255, 255, 0.05)",
                "cancel_hover": "rgba(255, 255, 255, 0.1)",
                "cancel_border": "rgba(255, 255, 255, 0.1)",
                "cancel_text": p.get("on_surface_variant", "#aaaaaa"),
                "mockup_bg": "rgba(0, 0, 0, 0.2)",
                "mockup_border": "rgba(255, 255, 255, 0.05)",
                "repo_bg": "rgba(255, 255, 255, 0.06)",
                "repo_hover_bg": "rgba(255, 255, 255, 0.12)",
                "repo_text": "rgba(255, 255, 255, 0.5)",
                "repo_hover_text": "rgba(255, 255, 255, 0.8)",
                "repo_border": "rgba(255, 255, 255, 0.1)",
                "tooltip_bg": "rgba(15, 17, 26, 0.95)",
                "tooltip_border": "rgba(255, 255, 255, 0.1)",
                "separator_bg": "rgba(255, 255, 255, 0.07)",
                "swatch_border": "rgba(255, 255, 255, 0.2)",
                "chevron_path": chevron_path,
            }
        else:
            colors = {
                "text_primary": p.get("on_background", "#1a1c23"),
                "text_secondary": p.get("on_surface_variant", "#4a4f68"),
                "accent_color": p.get("primary", "#2f64ff"),
                "card_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 255, 255, 0.85), stop:1 rgba(240, 242, 248, 0.95))",
                "card_border": "rgba(0, 0, 0, 0.08)",
                "checkbox_bg": "rgba(0, 0, 0, 0.05)",
                "checkbox_hover": "rgba(0, 0, 0, 0.08)",
                "checkbox_border": "rgba(0, 0, 0, 0.1)",
                "combo_bg": "rgba(255, 255, 255, 0.6)",
                "combo_hover_bg": "rgba(255, 255, 255, 0.8)",
                "combo_border": "rgba(0, 0, 0, 0.1)",
                "menu_bg": p.get("background", "rgba(250, 250, 255, 0.95)"),
                "menu_border": "rgba(0, 0, 0, 0.1)",
                "menu_item_hover": "rgba(0, 0, 0, 0.05)",
                "cancel_bg": "rgba(0, 0, 0, 0.03)",
                "cancel_hover": "rgba(0, 0, 0, 0.06)",
                "cancel_border": "rgba(0, 0, 0, 0.1)",
                "cancel_text": p.get("on_surface_variant", "#555555"),
                "mockup_bg": "rgba(255, 255, 255, 0.5)",
                "mockup_border": "rgba(0, 0, 0, 0.05)",
                "repo_bg": "rgba(0, 0, 0, 0.04)",
                "repo_hover_bg": "rgba(0, 0, 0, 0.08)",
                "repo_text": "rgba(0, 0, 0, 0.5)",
                "repo_hover_text": "rgba(0, 0, 0, 0.8)",
                "repo_border": "rgba(0, 0, 0, 0.1)",
                "tooltip_bg": "rgba(250, 250, 255, 0.95)",
                "tooltip_border": "rgba(0, 0, 0, 0.1)",
                "separator_bg": "rgba(0, 0, 0, 0.06)",
                "swatch_border": "rgba(0, 0, 0, 0.15)",
                "chevron_path": chevron_path,
            }

        # Load extracted QSS templates
        qss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "styles", "settings_dialog.qss"))
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
            self.setStyleSheet(Template(stylesheet).safe_substitute(colors))

            # Update Preview Swatches
            if hasattr(self, "primary_swatch") and "accent_color" in colors:
                self.primary_swatch.setStyleSheet(f"#Swatch0 {{ background-color: {colors['accent_color']}; border-radius: 12px; border: 2px solid {colors['swatch_border']}; }}")
            if hasattr(self, "bg_swatch") and "text_primary" in colors:
                self.bg_swatch.setStyleSheet(f"#Swatch1 {{ background-color: {colors.get('menu_bg', '#121212')}; border-radius: 12px; border: 2px solid {colors['accent_color']}; }}")

            # Update Mockup and Glow
            if hasattr(self, "save_glow") and "accent_color" in colors:
                accent = QColor(colors["accent_color"])
                accent.setAlpha(180 if is_dark else 100)
                self.save_glow.setColor(accent)

            if hasattr(self, "mockup_preview"):
                # Mockup is static image, but we can tint it
                pass
        else:
            logger.warning(f"Extracted QSS not found at {qss_path}. Reverting to no style.")

    def _on_profile_changed(self, text):
        self.update_stylesheet()

    def setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(32, 28, 32, 28)
        self._main_layout.setSpacing(16)

        self._build_header()
        self._build_main_card()
        # Horizontal layout for the bottom two-column section
        self._build_bottom_section()

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
        grid.setVerticalSpacing(16)
        grid.setHorizontalSpacing(24)
        grid.setContentsMargins(24, 24, 24, 24)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        main_card.setGraphicsEffect(shadow)

        grid.setSpacing(15)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        # Theme Mode
        mode_label = QLabel("Theme Mode:")
        mode_label.setFixedWidth(120)
        grid.addWidget(mode_label, 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Dark", "Light"])
        self.mode_combo.setFixedHeight(38)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.mode_combo, 0, 1)

        # Contrast Level
        contrast_label = QLabel("Contrast Level:")
        contrast_label.setFixedWidth(120)
        grid.addWidget(contrast_label, 1, 0)
        self.contrast_combo = QComboBox()
        self.contrast_combo.addItems(["Low", "Standard", "High"])
        self.contrast_combo.setFixedHeight(38)
        self.contrast_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.contrast_combo, 1, 1)

        # Theme Style
        style_label = QLabel("Theme Style:")
        style_label.setFixedWidth(120)
        grid.addWidget(style_label, 2, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(
            [
                "Auto (Smart)",
                "Neon Glass",
                "Frosted Glass",
                "Material Pure",
            ]
        )
        self.profile_combo.setFixedHeight(38)
        self.profile_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        grid.addWidget(self.profile_combo, 2, 1)

        grid.setRowStretch(4, 1)
        self._main_layout.addWidget(main_card)

    def _build_bottom_section(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        self._build_features_card(bottom_layout)
        self._build_preview_card(bottom_layout)

        self._main_layout.addLayout(bottom_layout)

    def _build_features_card(self, parent_layout):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("FEATURES")
        label.setObjectName("Subtitle")
        label.setStyleSheet("margin-bottom: 10px; font-weight: 800; letter-spacing: 1px;")
        layout.addWidget(label)

        def add_feature(icon_name, text, attr_name):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)

            icon_lbl = QLabel()
            icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons", icon_name)
            if os.path.exists(icon_path):
                # Tint the icon to white for premium look
                pix = QIcon(icon_path).pixmap(24, 24)
                tinted = QPixmap(pix.size())
                tinted.fill(Qt.transparent)
                painter = QPainter(tinted)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.drawPixmap(0, 0, pix)
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(tinted.rect(), QColor(255, 255, 255, 200)) # Muted white
                painter.end()
                icon_lbl.setPixmap(tinted)
            row.addWidget(icon_lbl)

            label = QLabel(text)
            label.setObjectName("FeatureLabel")
            label.setWordWrap(True)
            label.setMinimumHeight(35)
            row.addWidget(label)

            row.addStretch()

            check = QCheckBox()
            check.setCursor(Qt.PointingHandCursor)
            setattr(self, attr_name, check)
            row.addWidget(check)

            layout.addLayout(row)

        add_feature("monitor.svg", "Enable Kvantum Window Theming", "kvantum_check")
        add_feature("terminal-icon.svg", "Enable Konsole Profile Gen", "konsole_check")
        add_feature("shield.svg", "Enable SDDM Login Sync", "sddm_check")

        layout.addStretch(1)

        # About / Repo section at the bottom
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background: rgba(255,255,255,0.07); max-height: 1px; margin: 4px 0px;")
        layout.addWidget(separator)

        about_row = QHBoxLayout()
        version_lbl = QLabel("v1.0 · Adaptive Cachy Beauty")
        version_lbl.setStyleSheet("color: #888888; font-size: 11px; font-weight: 500;")
        about_row.addWidget(version_lbl)
        about_row.addStretch()

        repo_btn = QPushButton("GitHub ↗")
        repo_btn.setObjectName("RepoBtn")
        repo_btn.setFixedSize(80, 24)
        repo_btn.setCursor(Qt.PointingHandCursor)
        repo_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/dimarch0x/adaptive-cachy-beauty")
            )
        )
        about_row.addWidget(repo_btn)
        layout.addLayout(about_row)

        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)

        parent_layout.addWidget(card, 1)

    def _build_preview_card(self, parent_layout):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Theme Preview")
        label.setObjectName("Subtitle")
        label.setStyleSheet("margin-bottom: 20px; font-weight: 800; letter-spacing: 0.5px;")
        layout.addWidget(label)

        # Swatches Row
        swatch_layout = QHBoxLayout()
        self.primary_swatch = QLabel()
        self.primary_swatch.setObjectName("Swatch0")
        self.primary_swatch.setFixedSize(50, 50)
        self.primary_swatch.setToolTip("Primary Accent")
        swatch_layout.addWidget(self.primary_swatch)

        self.bg_swatch = QLabel()
        self.bg_swatch.setObjectName("Swatch1")
        self.bg_swatch.setFixedSize(50, 50)
        self.bg_swatch.setToolTip("Background Mood")
        swatch_layout.addWidget(self.bg_swatch)
        swatch_layout.addStretch()
        layout.addLayout(swatch_layout)

        layout.addSpacing(16)

        # Desktop Mockup Container
        self.mockup = QFrame()
        self.mockup.setObjectName("Mockup")
        self.mockup.setMinimumHeight(110)

        mockup_layout = QVBoxLayout(self.mockup)
        mockup_layout.setContentsMargins(0, 10, 0, 0)

        self.mockup_preview = QLabel()
        img_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "textures", "ui_preview.png")
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaledToWidth(145, Qt.SmoothTransformation)
            self.mockup_preview.setPixmap(pix)
        self.mockup_preview.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        mockup_layout.addWidget(self.mockup_preview, 0, Qt.AlignBottom | Qt.AlignCenter)

        layout.addWidget(self.mockup, 1)

        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        parent_layout.addWidget(card, 1)

    def _build_actions(self):
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setFixedSize(120, 36)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save && Apply")
        self.save_btn.setFixedSize(160, 36)
        self.save_btn.clicked.connect(self.save_settings)

        # Glow Effect for Save Button
        save_glow = QGraphicsDropShadowEffect(self)
        save_glow.setBlurRadius(25)
        save_glow.setOffset(0, 0)
        save_glow.setColor(QColor(109, 178, 255, 180)) # Default glow
        self.save_btn.setGraphicsEffect(save_glow)
        self.save_glow = save_glow # Store reference to update color later

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        self._main_layout.addLayout(btn_layout)

    def _apply_popup_transparency(self):
        for combo in (self.mode_combo, self.contrast_combo, self.profile_combo):
            combo.setItemDelegate(QStyledItemDelegate(combo))
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
        self.sddm_check.setChecked(bool(self.config.get("enable_sddm", True)))
        self.mode_combo.setCurrentText(self.config.get("theme_mode", "Dark"))

    def save_settings(self):
        is_dark = self.mode_combo.currentText() == "Dark"
        self.config.set("dark_mode", is_dark)

        self.config.set("contrast_level", self.contrast_combo.currentText().lower())
        self.config.set("theme_style", self.profile_combo.currentText())
        self.config.set("enable_kvantum", self.kvantum_check.isChecked())
        self.config.set("enable_konsole", self.konsole_check.isChecked())
        self.config.set("enable_sddm", self.sddm_check.isChecked())
        self.config.set("theme_mode", self.mode_combo.currentText())

        logger.info("User settings saved from Settings Dialog.")
        self.settings_saved.emit()
        self.accept()
