import json
from pathlib import Path


SETTINGS_PATH = Path(__file__).resolve().with_name("user_settings.json")
DEFAULT_SETTINGS = {
    "provider": "groq",
    "groq_model": "llama-3.3-70b-versatile",
    "google_model": "gemini-2.5-flash",
}


def load_settings():
    if not SETTINGS_PATH.exists():
        return dict(DEFAULT_SETTINGS)

    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_SETTINGS)

    settings = dict(DEFAULT_SETTINGS)
    if isinstance(data, dict):
        settings.update(data)
    return settings


def save_settings(settings):
    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings)
    SETTINGS_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")


def get_selected_provider():
    provider = load_settings().get("provider", "groq")
    return provider if provider in {"groq", "google"} else "groq"


def set_selected_provider(provider):
    normalized = provider if provider in {"groq", "google"} else "groq"
    save_settings({"provider": normalized})
    return normalized


def get_selected_model(provider):
    settings = load_settings()
    if provider == "google":
        return settings.get("google_model", DEFAULT_SETTINGS["google_model"])
    return settings.get("groq_model", DEFAULT_SETTINGS["groq_model"])


def set_selected_model(provider, model):
    if provider == "google":
        save_settings({"google_model": model})
    else:
        save_settings({"groq_model": model})
    return model
