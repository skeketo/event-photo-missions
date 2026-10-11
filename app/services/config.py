import json
import os
from pathlib import Path

CONFIG_FILE = Path("/app/data/app_config.json")

ALLOWED_EVENT_TYPES = [
    "wedding",
    "birthday",
    "company",
    "party",
    "communion",
    "custom",
]

DEFAULT_CONFIG = {
    "APP_NAME": "Event Photo Missions",
    "EVENT_DATE": "Event date",
    "EVENT_TYPE": "wedding",
    "EVENT_HOSTS": "los protagonistas",
    "EVENT_LABEL": "evento",
    "PROTAGONISTS_LABEL": "protagonistas",
    "PRIZE_TEXT": "el premio indicado por los organizadores",
    "LEGAL_TEXT": "Al subir fotos o vídeos aceptas compartirlos con los organizadores para uso privado como recuerdo del evento.",
    "PUBLIC_BASE_URL": "http://localhost:8093",
    "APP_LANGUAGE": "es",
}


def _env_default(key):
    return os.getenv(key, DEFAULT_CONFIG.get(key, ""))


def get_config():
    config = {key: _env_default(key) for key in DEFAULT_CONFIG}

    if CONFIG_FILE.exists():
        try:
            saved = json.loads(CONFIG_FILE.read_text())
            for key in DEFAULT_CONFIG:
                if key in saved:
                    config[key] = str(saved[key])
        except Exception:
            pass

    if config.get("EVENT_TYPE") not in ALLOWED_EVENT_TYPES:
        config["EVENT_TYPE"] = "custom"

    return config


def get_setting(key, default=""):
    return get_config().get(key, default)


def save_config(new_config):
    current = get_config()

    for key in DEFAULT_CONFIG:
        if key in new_config:
            current[key] = str(new_config[key]).strip()

    if current.get("EVENT_TYPE") not in ALLOWED_EVENT_TYPES:
        current["EVENT_TYPE"] = "custom"

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(current, indent=2, ensure_ascii=False)
    )

    return current
