
from modules.story_intelligence.config import get_settings

settings = get_settings()

print("Configuration loaded successfully!")
print("API key exists:", bool(
    settings.gemini_api_key.get_secret_value()
))
print("Model:", settings.gemini_model)
