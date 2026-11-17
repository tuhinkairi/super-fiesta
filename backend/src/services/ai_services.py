"""Application-level orchestration for AI model operations."""

from src.models.ai_model import AIModel


def get_ai_model(app) -> AIModel:
    model = app.state.ai_models
    if model is None:
        try:
            model = AIModel()
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                "AI is not configured. Install the AI module dependencies and set GEMINI_API_KEY."
            ) from exc
        app.state.ai_models = model
    return model
