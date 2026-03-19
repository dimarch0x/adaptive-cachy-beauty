import sys
import os

# Force X11/XWayland to enable KWin Blur via xprop
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QCoreApplication, QTimer, QObject, Slot, SLOT
from PySide6.QtDBus import QDBusConnection

from core.wallpaper_analyzer import WallpaperAnalyzer
from core.theme_generator import ThemeGenerator
from integrations.plasma_theme_manager import PlasmaThemeManager
from integrations.kvantum_generator import KvantumGenerator
from integrations.terminal_theme_manager import TerminalThemeManager
from ui.settings_dialog import SettingsDialog
from config_manager import ConfigManager
from logger import logger


class BeautyEngineTray(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = ConfigManager()
        self.settings_dialog = None

        self.analyzer = WallpaperAnalyzer()
        self.generator = ThemeGenerator()
        self.theme_manager = PlasmaThemeManager()
        self.kvantum_generator = KvantumGenerator()
        self.terminal_theme_manager = TerminalThemeManager()

        # Create the tray icon
        self.icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "icon.png")
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("Adaptive Cachy Beauty")

        if os.path.exists(self.icon_path):
             self.tray.setIcon(QIcon(self.icon_path))
        else:
            # Fallback to a standard icon for MVP if custom icon doesn't exist
            self.tray.setIcon(
                QIcon.fromTheme(
                    "preferences-desktop-theme", QIcon.fromTheme("document-new")
                )
            )

        # Create the menu
        self.menu = QMenu()

        # Add actions
        self.refresh_action = QAction("Refresh Theme", self.app)
        self.refresh_action.triggered.connect(self.refresh_theme)
        self.menu.addAction(self.refresh_action)

        self.settings_action = QAction("Settings...", self.app)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        self.quit_action = QAction("Quit", self.app)
        self.quit_action.triggered.connect(QCoreApplication.instance().quit)
        self.menu.addAction(self.quit_action)

        # Add menu to tray and show
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        # Debounce timer for wallpaper changes
        self.refresh_timer = QTimer(self.app)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.setInterval(2000)  # 2 seconds debounce
        self.refresh_timer.timeout.connect(self.refresh_theme)

        self.setup_dbus()

    def setup_dbus(self):
        """Connects to KDE Plasma DBus to listen for wallpaper changes."""
        bus = QDBusConnection.sessionBus()
        success = bus.connect(
            "org.kde.plasmashell",
            "/PlasmaShell",
            "org.kde.PlasmaShell",
            "wallpaperChanged",
            self,
            SLOT("on_wallpaper_changed()"),
        )
        if success:
            logger.info(
                "Successfully connected to Plasma DBus wallpaperChanged signal."
            )
        else:
            logger.warning("Failed to connect to Plasma DBus signal.")

    @Slot()
    def on_wallpaper_changed(self):
        logger.debug(
            "DBus signal received: wallpaperChanged. Starting debounce timer."
        )
        self.refresh_timer.start()

    def refresh_theme(self):
        self.tray.showMessage(
            "Beauty Engine", "Analyzing wallpaper...", QSystemTrayIcon.Information, 2000
        )
        logger.info("Refresh theme triggered. Analysis starting...")
        wallpaper_path = self.analyzer.get_current_wallpaper_path()
        if not wallpaper_path:
            self.tray.showMessage(
                "Error", "Failed to get wallpaper path.", QSystemTrayIcon.Warning
            )
            logger.error("Failed to get wallpaper path.")
            return

        logger.info(f"Current Wallpaper: {wallpaper_path}")

        try:
            is_dark = self.config.get("dark_mode", True)
            style = self.config.get("theme_style", "Neon Glass")
            contrast_level = self.config.get("contrast_level", "standard") # Read it
            palette = self.generator.generate_material_you_palette(
                wallpaper_path, is_dark=is_dark, style=style, contrast_level=contrast_level
            )
            logger.info(
                f"Generated {'Dark' if is_dark else 'Light'} {style} Palette: {palette}"
            )

            # Show a sample of the palette to the user
            colors_str = f"Primary: {palette['primary']}\nBg: {palette['background']}"
            self.tray.showMessage(
                "Applying Theme",
                f"Colors extracted!\n{colors_str}",
                QSystemTrayIcon.Information,
                2000,
            )

            # Apply to Plasma
            self.theme_manager.generate_and_apply_theme(
                palette, theme_name="AdaptiveCachy"
            )

            # Apply to Konsole
            if self.config.get("enable_konsole", True):
                self.theme_manager.generate_konsole_theme(
                    palette, theme_name="AdaptiveCachy"
                )

            # Apply to Kvantum
            if self.config.get("enable_kvantum", True):
                self.kvantum_generator.generate_and_apply(palette)

            # Apply to Terminals (Alacritty/Kitty)
            if self.config.get("enable_terminals", True):
                self.terminal_theme_manager.apply_themes(palette, style=style)

            self.tray.showMessage(
                "Success",
                "Theme applied successfully!",
                QSystemTrayIcon.Information,
                3000,
            )
            logger.info("Application flow completed successfully.")

        except Exception as e:
            logger.exception(f"Error generating theme: {e}")
            self.tray.showMessage(
                "Error", f"Failed to generate theme: {e}", QSystemTrayIcon.Critical
            )

    def open_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.config)
            self.settings_dialog.settings_saved.connect(self.refresh_theme)

        # Bring to front
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    tray_app = BeautyEngineTray()
    tray_app.run()
