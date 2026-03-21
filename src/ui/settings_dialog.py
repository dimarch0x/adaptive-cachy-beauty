import os
import math
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
    QWidget,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QSizePolicy,
    QStyledItemDelegate,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QUrl,
    QPoint,
)
from PySide6.QtGui import (
    QIcon,
    QPainter,
    QColor,
    QPixmap,
    QDesktopServices,
    QPen,
    QPainterPath,
)

from config_manager import ConfigManager
from logger import logger


class CloseButton(QPushButton):
    """Custom painted close button — theme-aware SVG visible on any background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("AppCloseBtn")
        self._hovered = False
        self._color = QColor(255, 255, 255)

    def set_color(self, color_str):
        self._color = QColor(color_str)
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        cx, cy = self.width() / 2, self.height() / 2

        # Hover: draw red background circle centered
        if self._hovered:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(220, 60, 60, 150))
            r_circle = (side - 2) / 2
            p.drawEllipse(QPoint(cx, cy), r_circle, r_circle)

        # Draw X lines perfectly centered
        margin = 10
        half_cross = (side - margin * 2) / 2

        pen = QPen(self._color, 2.2, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)

        # Line 1: Top-Left to Bottom-Right
        p.drawLine(cx - half_cross, cy - half_cross, cx + half_cross, cy + half_cross)
        # Line 2: Top-Right to Bottom-Left
        p.drawLine(cx + half_cross, cy - half_cross, cx - half_cross, cy + half_cross)
        p.end()


class SettingsHeader(QFrame):
    """Custom draggable Header Bar (CSD)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None
        self.setObjectName("AppHeader")
        self.setFixedHeight(45)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        icon_lbl = QLabel()
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.png"
        )
        if os.path.exists(icon_path):
            icon_lbl.setPixmap(
                QPixmap(icon_path).scaled(
                    18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        icon_lbl.setObjectName("AppIcon")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel("Beauty Engine Settings")
        title_lbl.setObjectName("AppTitle")
        layout.addWidget(title_lbl)

        layout.addStretch()

        close_btn = CloseButton(self)
        close_btn.clicked.connect(self.window().close)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.window().move(self.window().pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()


class AnimatedToggle(QCheckBox):
    """Custom iOS/Android style animated toggle switch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 24)
        self.setCursor(Qt.PointingHandCursor)

        self._accent_color = QColor("#9ece6a")  # Default placeholder
        self._thumb_position = 0.0

        self.animation = QPropertyAnimation(self, b"thumbPosition")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(250)

        self.stateChanged.connect(self._setup_animation)

    def _setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(1.0)
        else:
            self.animation.setEndValue(0.0)
        self.animation.start()

    @Property(float)
    def thumbPosition(self):
        return self._thumb_position

    @thumbPosition.setter
    def thumbPosition(self, pos):
        self._thumb_position = pos
        self.update()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        off_bg = QColor(120, 120, 120, 100)  # Muted OFF grey

        # Lerp color from off_bg to _accent_color
        r = (
            off_bg.red()
            + (self._accent_color.red() - off_bg.red()) * self._thumb_position
        )
        g = (
            off_bg.green()
            + (self._accent_color.green() - off_bg.green()) * self._thumb_position
        )
        b = (
            off_bg.blue()
            + (self._accent_color.blue() - off_bg.blue()) * self._thumb_position
        )
        a = (
            off_bg.alpha()
            + (self._accent_color.alpha() - off_bg.alpha()) * self._thumb_position
        )

        current_bg = QColor(int(r), int(g), int(b), int(a))

        p.setPen(Qt.NoPen)
        p.setBrush(current_bg)

        rect = self.contentsRect()
        track_radius = rect.height() / 2
        p.drawRoundedRect(rect, track_radius, track_radius)

        p.setBrush(QColor("#ffffff"))
        thumb_radius = track_radius - 2
        thumb_range = rect.width() - (thumb_radius * 2) - 4
        current_x = 2 + (thumb_range * self._thumb_position)

        # Draw the thumb circle
        p.drawEllipse(int(current_x), 2, int(thumb_radius * 2), int(thumb_radius * 2))
        p.end()

    def update_accent(self, hex_color):
        self._accent_color = QColor(hex_color)
        if self.isChecked():
            self._thumb_position = 1.0
        self.update()


class SettingsDialog(QDialog):
    settings_saved = Signal()  # Signal emitted when settings are saved

    # --- Glass configuration per style ---
    _GLASS_PROFILES = {
        "Neon Glass": {"alpha": 191, "frost_opacity": 0.06, "blur": True},
        "Frosted Glass": {"alpha": 153, "frost_opacity": 0.12, "blur": True},
        "Material Pure": {"alpha": 255, "frost_opacity": 0.0, "blur": False},
    }
    _BASE_RGB = (15, 17, 26)  # Dark background base

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.current_palette = self.config.get("cached_palette", None)

        self.setWindowTitle("Beauty Engine Settings")

        # Load custom app icon
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "icons", "icon.png"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(640, 695)
        self.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint
        )
        # Always keep translucent — we control opacity via paintEvent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._window_radius = 16  # Dynamic radius depending on style

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
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "textures",
            "frost_noise.png",
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
                import math

                # Aesthetic trade-off: to completely avoid the X11 Plasma Kornerbug,
                # we use a strict rectangular (0px radius) shape when glass blur is active.
                # A sharp floating glass pane natively matches its X11 region.
                subprocess.run(
                    [
                        "xprop",
                        "-f",
                        "_KDE_NET_WM_BLUR_BEHIND_REGION",
                        "32c",
                        "-set",
                        "_KDE_NET_WM_BLUR_BEHIND_REGION",
                        "0",
                        "-id",
                        wid,
                    ],
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
        # Use dynamic radius: 0 for glass, 16 for pure material
        r = getattr(self, "_window_radius", 0)
        painter.drawRoundedRect(self.rect(), r, r)

        # 2) Draw frost noise overlay (tiled) with current opacity
        if self._frost_opacity > 0.01 and not self._frost_pixmap.isNull():
            # Clip the noise so it doesn't bleed out of the rounded corners!
            path = QPainterPath()
            path.addRoundedRect(self.rect(), r, r)
            painter.setClipPath(path)

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
        chevron_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "resources",
                "icons",
                "chevron-down.svg",
            )
        )
        chevron_path = chevron_path.replace("\\", "/")

        try:
            current_style = self.profile_combo.currentText()
        except AttributeError:
            current_style = ""

        # Resolve glass profile for this style
        profile = self._GLASS_PROFILES.get(
            current_style, self._GLASS_PROFILES["Material Pure"]
        )
        target_alpha = profile["alpha"]
        target_frost = profile["frost_opacity"]

        # Animate background opacity
        self._alpha_anim.stop()
        self._alpha_anim.setStartValue(self._bg_alpha)
        self._alpha_anim.setEndValue(target_alpha)
        self._alpha_anim.start()

        # Toggle dynamic radius
        self._window_radius = 0 if profile["blur"] else 16

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

        is_pure = current_style == "Material Pure"

        if is_dark:
            c_bg = "#24283B" if is_pure else "rgba(255, 255, 255, 0.05)"
            c_border = "#2F3549" if is_pure else "rgba(255, 255, 255, 0.08)"
            h_border = "#2F3549" if is_pure else "rgba(255, 255, 255, 0.1)"
            h_top_border = "none" if is_pure else "1px solid rgba(255, 255, 255, 0.2)"

            colors = {
                "text_primary": p.get("on_background", "#ffffff"),
                "text_secondary": p.get("on_surface_variant", "#a9b1d6"),
                "accent_color": p.get("primary", "#2f64ff"),
                "error_color": p.get("error", "#ff5555"),
                "card_bg": c_bg,
                "card_border": c_border,
                "header_border": h_border,
                "header_top_border": h_top_border,
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
                "window_radius": f"{self._window_radius}px",
            }
        else:
            c_bg = "#FFFFFF" if is_pure else "rgba(255, 255, 255, 0.6)"
            c_border = "#D1D8E0" if is_pure else "rgba(0, 0, 0, 0.08)"
            h_border = "#D1D8E0" if is_pure else "rgba(0, 0, 0, 0.1)"
            h_top_border = "none" if is_pure else "2px solid rgba(255, 255, 255, 0.6)"

            colors = {
                "text_primary": p.get("on_background", "#1a1c23"),
                "text_secondary": p.get("on_surface_variant", "#4a4f68"),
                "accent_color": p.get("primary", "#2f64ff"),
                "error_color": p.get("error", "#cc0000"),
                "card_bg": c_bg,
                "card_border": c_border,
                "header_border": h_border,
                "header_top_border": h_top_border,
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
                "window_radius": f"{self._window_radius}px",
            }

        # Load extracted QSS templates
        qss_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "resources",
                "styles",
                "settings_dialog.qss",
            )
        )
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
            self.setStyleSheet(Template(stylesheet).safe_substitute(colors))

            # Update Preview Swatches
            if hasattr(self, "primary_swatch") and "accent_color" in colors:
                self.primary_swatch.setStyleSheet(
                    f"#Swatch0 {{ background-color: {colors['accent_color']}; border-radius: 12px; border: 2px solid {colors['swatch_border']}; }}"
                )
            if hasattr(self, "bg_swatch") and "text_primary" in colors:
                self.bg_swatch.setStyleSheet(
                    f"#Swatch1 {{ background-color: {colors.get('menu_bg', '#121212')}; border-radius: 12px; border: 2px solid {colors['accent_color']}; }}"
                )

            # Update Mockup and Glow
            if hasattr(self, "save_glow") and "accent_color" in colors:
                accent = QColor(colors["accent_color"])
                accent.setAlpha(180 if is_dark else 100)
                self.save_glow.setColor(accent)

            if hasattr(self, "mockup_preview"):
                # Mockup is static image, but we can tint it
                pass

            # Toggle card shadows
            for shadow_attr in [
                "main_card_shadow",
                "features_card_shadow",
                "preview_card_shadow",
            ]:
                card_shadow = getattr(self, shadow_attr, None)
                if card_shadow:
                    card_shadow.setEnabled(not is_pure)

            # App Icon Neon Glow and Close Button Color
            if hasattr(self, "header_bar"):
                icon_lbl = self.header_bar.findChild(QLabel, "AppIcon")
                if icon_lbl:
                    if current_style == "Neon Glass" and "accent_color" in colors:
                        glow = QGraphicsDropShadowEffect(self)
                        glow.setBlurRadius(20)
                        glow.setOffset(0, 0)
                        accent = QColor(colors["accent_color"])
                        accent.setAlpha(180)
                        glow.setColor(accent)
                        icon_lbl.setGraphicsEffect(glow)
                    else:
                        icon_lbl.setGraphicsEffect(None)

                close_btn = self.header_bar.findChild(CloseButton, "AppCloseBtn")
                if close_btn:
                    close_btn.set_color(colors.get("text_primary", "#ffffff"))

            # Sub-widget Accent Color Injection
            for toggle_attr in ["kvantum_check", "konsole_check", "sddm_check"]:
                toggle = getattr(self, toggle_attr, None)
                if hasattr(toggle, "update_accent"):
                    toggle.update_accent(colors.get("accent_color", "#74B816"))
        else:
            logger.warning(
                f"Extracted QSS not found at {qss_path}. Reverting to no style."
            )

    def _on_profile_changed(self, text):
        self.update_stylesheet()

    def setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 1. Custom Header Bar
        self.header_bar = SettingsHeader(self)
        self._main_layout.addWidget(self.header_bar)

        # 2. Main content container (to keep paddings)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(32, 20, 32, 28)
        self.content_layout.setSpacing(16)

        self._build_header()
        self._build_main_card()
        # Horizontal layout for the bottom two-column section
        self._build_bottom_section()

        self.content_layout.addStretch()
        self._build_actions()

        self._main_layout.addWidget(self.content_widget)
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

        self.content_layout.addLayout(header_layout)

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
        self.main_card_shadow = shadow

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
        self.content_layout.addWidget(main_card)

    def _build_bottom_section(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        self._build_features_card(bottom_layout)
        self._build_preview_card(bottom_layout)

        self.content_layout.addLayout(bottom_layout)

    def _build_features_card(self, parent_layout):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("FEATURES")
        label.setObjectName("Subtitle")
        label.setStyleSheet(
            "margin-bottom: 10px; font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(label)

        def add_feature(icon_name, text, attr_name):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)

            icon_lbl = QLabel()
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "resources", "icons", icon_name
            )
            if os.path.exists(icon_path):
                # Tint the icon to white for premium look
                pix = QIcon(icon_path).pixmap(24, 24)
                tinted = QPixmap(pix.size())
                tinted.fill(Qt.transparent)
                painter = QPainter(tinted)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.drawPixmap(0, 0, pix)
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(
                    tinted.rect(), QColor(255, 255, 255, 200)
                )  # Muted white
                painter.end()
                icon_lbl.setPixmap(tinted)
            row.addWidget(icon_lbl)

            label = QLabel(text)
            label.setObjectName("FeatureLabel")
            label.setWordWrap(True)
            label.setMinimumHeight(35)
            row.addWidget(label)

            row.addStretch()

            check = AnimatedToggle()
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
        separator.setStyleSheet(
            "background: rgba(255,255,255,0.07); max-height: 1px; margin: 4px 0px;"
        )
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
        self.features_card_shadow = shadow

        parent_layout.addWidget(card, 1)

    def _build_preview_card(self, parent_layout):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Theme Preview")
        label.setObjectName("Subtitle")
        label.setStyleSheet(
            "margin-bottom: 20px; font-weight: 800; letter-spacing: 0.5px;"
        )
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
        img_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "textures",
            "ui_preview.png",
        )
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
        self.preview_card_shadow = shadow

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
        save_glow.setColor(QColor(109, 178, 255, 180))  # Default glow
        self.save_btn.setGraphicsEffect(save_glow)
        self.save_glow = save_glow  # Store reference to update color later

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        self.content_layout.addLayout(btn_layout)

    def _apply_popup_transparency(self):
        for combo in (self.mode_combo, self.contrast_combo, self.profile_combo):
            combo.setItemDelegate(QStyledItemDelegate(combo))
            container = combo.view().parentWidget()
            if container:
                container.setWindowFlags(
                    Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
                )
                container.setAttribute(Qt.WA_TranslucentBackground)
                container.setObjectName("ComboContainer")
                container.setStyleSheet(
                    "#ComboContainer { background: transparent; border: none; }"
                )

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
