import json
import sys
from pathlib import Path
from consts import *

IS_WEB = sys.platform in ("emscripten", "wasi")

_DEFAULTS  = {
    "music_volume": 0.25,
    "sfx_volume": 0.25,
    "difficulty": 0.5, 
}

_STORAGE_KEY = f"{GAME_NAME}_settings"

class saveManager: 

    def __init__(self):
        self._data = self._readRaw() or {}
        self.hasSave = bool(self._data)

        self.musicSettings = self._data.get("music_volume", _DEFAULTS["music_volume"])
        self.sfxSettings = self._data.get("sfx_volume", _DEFAULTS["sfx_volume"])
        self.difficulty = self._data.get("difficulty", _DEFAULTS["difficulty"])

        self._settings_cache = None

    def set_settings(
            self, 
            musicSettings=None, 
            sfxSettings=None,
            difficulty=None
            ):
        self.hasSave = True
        if musicSettings is not None:
            self.musicSettings = musicSettings
            self._set("music_volume", musicSettings)
        if sfxSettings is not None:
            self.sfxSettings = sfxSettings
            self._set("sfx_volume", sfxSettings) 
        if difficulty is not None:
            self.difficulty = difficulty
            self._set("difficulty", difficulty) 

        self._settings_cache = None

    def _set(self, key, value):
        self._data[key] = value
        try:
            self._writeRaw(self._data)
        except Exception as e:
            print(f" save failed: {e}")

    def _get(self, key, default=None):
        return self._data.get(key, default)

    def get_settings(self) -> dict[str, float]:
        if self._settings_cache is None:
            self._settings_cache = {
                "music_volume": self.musicSettings,
                "sfx_volume": self.sfxSettings,
                "difficulty": self.difficulty,
            }
        return self._settings_cache

    def _desktopPath(self):
        try:
            from platformdirs import user_config_dir
            d = Path(user_config_dir(GAME_NAME, "YourStudio"))
        except ImportError:
            d = Path.home() / f".{GAME_NAME}"
        d.mkdir(parents=True, exist_ok=True)
        return d / "save.json"

    def _readRaw(self):
        try:
            if IS_WEB:
                from platform import window
                raw = window.localStorage.getItem(_STORAGE_KEY)
                return json.loads(raw) if raw else None
            else:
                path = self._desktopPath()
                if path.exists():
                    return json.loads(path.read_text())
                return None
        except Exception as e:
            print(f"load failed, using defaults: {e}")
            return None

    def _writeRaw(self, data):
        if IS_WEB:
            from platform import window
            window.localStorage.setItem(_STORAGE_KEY, json.dumps(data))
        else:
            path = self._desktopPath()
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2))
            tmp.replace(path)