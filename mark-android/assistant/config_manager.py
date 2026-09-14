"""
config_manager.py
------------------
Adaptiert von Mark LIII (memory/config_manager.py). Statt eines beliebigen
Pfads unter config/api_keys.json nutzen wir den von Android vorgesehenen
privaten App-Speicher (Kivy: App.get_running_app().user_data_dir), damit die
Datei bei Deinstallation sauber mit entfernt wird und keine Speicher-
Berechtigung dafür nötig ist.
"""

import json
import os

_CONFIG_FILE = None
_DEFAULTS = {
    "api_key": "",
    "assistant_name": "Mark",
    "user_name": "Boss",
    "voice": "Puck",
    "ui_color": "#00E5FF",
    "wake_word_enabled": False,
    "brief_enabled": True,
}


def init(app_data_dir):
    """Muss einmal beim App-Start mit dem Android-App-Verzeichnis aufgerufen werden."""
    global _CONFIG_FILE
    os.makedirs(app_data_dir, exist_ok=True)
    _CONFIG_FILE = os.path.join(app_data_dir, "config.json")
    if not os.path.exists(_CONFIG_FILE):
        _save(_DEFAULTS.copy())


def _load():
    if _CONFIG_FILE is None or not os.path.exists(_CONFIG_FILE):
        return _DEFAULTS.copy()
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = _DEFAULTS.copy()
        merged.update(data)
        return merged
    except Exception:
        return _DEFAULTS.copy()


def _save(data):
    if _CONFIG_FILE is None:
        return
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get(key, default=None):
    return _load().get(key, default)


def set(key, value):
    data = _load()
    data[key] = value
    _save(data)


def get_api_key():
    return get("api_key", "")


def set_api_key(key):
    set("api_key", key)


def get_assistant_name():
    return get("assistant_name", "Mark")


def get_user_name():
    return get("user_name", "Boss")


def get_voice():
    return get("voice", "Puck")


def get_ui_color():
    return get("ui_color", "#00E5FF")
