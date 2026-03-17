import requests

from config import GOOGLE_API_KEY, GROQ_API_KEY
from gemini_client import GeminiClient
from groq_client import GroqClient


PROVIDER_LABELS = {
    "groq": "Groq",
    "google": "Google Gemini",
}

DEFAULT_MODELS = {
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
        "moonshotai/kimi-k2-instruct",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "groq/compound",
        "groq/compound-mini",
    ],
    "google": [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.5-pro",
        "gemini-pro-latest",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
        "gemini-3.1-flash-lite-preview",
    ],
}


class ProviderManager:
    def __init__(self):
        self._clients = {}
        self._model_cache = {provider: list(models) for provider, models in DEFAULT_MODELS.items()}

    def get_provider_label(self, provider):
        return PROVIDER_LABELS.get(provider, PROVIDER_LABELS["groq"])

    def get_default_model(self, provider):
        models = self.get_cached_models(provider)
        return models[0]

    def get_cached_models(self, provider):
        normalized = provider if provider in PROVIDER_LABELS else "groq"
        return list(self._model_cache.get(normalized, DEFAULT_MODELS[normalized]))

    def refresh_models(self, provider):
        normalized = provider if provider in PROVIDER_LABELS else "groq"
        if normalized == "google":
            models = self._fetch_google_models()
        else:
            models = self._fetch_groq_models()

        if models:
            self._model_cache[normalized] = models
        return self.get_cached_models(normalized)

    def get_client(self, provider, model=None):
        normalized = provider if provider in PROVIDER_LABELS else "groq"
        selected_model = model or self.get_default_model(normalized)
        cache_key = (normalized, selected_model)
        if cache_key not in self._clients:
            if normalized == "google":
                self._clients[cache_key] = GeminiClient(selected_model)
            else:
                self._clients[cache_key] = GroqClient(selected_model)
        return self._clients[cache_key]

    def _fetch_groq_models(self):
        if not GROQ_API_KEY:
            return []

        try:
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=4,
            )
            response.raise_for_status()
            payload = response.json()
            text_models = []
            for item in payload.get("data", []):
                model_id = item.get("id")
                if not model_id or model_id.startswith("whisper"):
                    continue
                if "guard" in model_id or "safeguard" in model_id:
                    continue
                text_models.append(model_id)
            return sorted(set(text_models))
        except requests.RequestException as error:
            print(f"Could not refresh Groq models: {error}")
            return []

    def _fetch_google_models(self):
        if not GOOGLE_API_KEY:
            return []

        try:
            response = requests.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": GOOGLE_API_KEY},
                timeout=4,
            )
            response.raise_for_status()
            payload = response.json()
            models = []
            for item in payload.get("models", []):
                methods = item.get("supportedGenerationMethods", [])
                name = item.get("name", "")
                if "generateContent" not in methods or not name.startswith("models/"):
                    continue
                model_name = name.split("/", 1)[1]
                if any(keyword in model_name for keyword in ("image", "tts", "robotics", "research", "computer-use", "banana")):
                    continue
                models.append(model_name)
            return sorted(set(models))
        except requests.RequestException as error:
            print(f"Could not refresh Google models: {error}")
            return []
