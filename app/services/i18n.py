import json
import os
from pathlib import Path

from services.config import get_setting

TRANSLATIONS_DIR = Path("/app/translations")

SUPPORTED_LANGUAGES = {
    "es": "Español",
    "en": "English",
    "fr": "Français",
}

DEFAULT_LANGUAGE = "es"


def current_language():
    lang = get_setting("APP_LANGUAGE", os.getenv("APP_LANGUAGE", DEFAULT_LANGUAGE))
    lang = str(lang).strip().lower()

    if lang not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE

    return lang


def _load_language(lang):
    path = TRANSLATIONS_DIR / f"{lang}.json"

    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def translations():
    lang = current_language()

    base = _load_language(DEFAULT_LANGUAGE)
    selected = _load_language(lang)

    merged = dict(base)
    merged.update(selected)

    return merged


def t(key, default=None):
    value = translations().get(key)

    if value is None:
        return default if default is not None else key

    return value


def language_context():
    return {
        "language": current_language(),
        "languages": SUPPORTED_LANGUAGES,
        "t": t,
    }
