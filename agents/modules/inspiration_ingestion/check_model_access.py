
from google import genai
from modules.story_intelligence.config import get_settings


def main():
    config = get_settings()
    model_name = config.gemini_model

    print(f"Checking access to {model_name}...\n")

    client = genai.Client(
        api_key=config.gemini_api_key.get_secret_value()
    )

    try:
        model = client.models.get(model=model_name)

        print("SUCCESS: Model is accessible!")
        print("Model:", model.name)
        print("Display name:", model.display_name)

    except Exception as error:
        print("\nMODEL ACCESS CHECK FAILED")
        print("Error type:", type(error).__name__)
        print("Error:", error)

    finally:
        client.close()


if __name__ == "__main__":
    main()
