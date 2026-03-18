import json
import os
from logger import logger


class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/adaptive-cachy-beauty")
        self.config_path = os.path.join(self.config_dir, "config.json")
        self.settings = {
            "dark_mode": True,
            "enable_kvantum": True,
            "enable_konsole": True,
            "contrast_level": "normal",
        }
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
                logger.info("Configuration loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.save_config()  # Create default
        else:
            self.save_config()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_config()
