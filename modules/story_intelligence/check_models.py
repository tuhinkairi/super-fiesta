
from modules.story_intelligence.llm.llm_client import LLMClient


def main():
    client = LLMClient()

    try:
        print("Configured model:", client.model)
        print("\nModels available to your API key:\n")

        for model in client.client.models.list():
            actions = getattr(model, "supported_actions", []) or []

            if "generateContent" in actions:
                print(model.name)

    except Exception as error:
        print("Could not retrieve models:")
        print(error)

    finally:
        client.close()


if __name__ == "__main__":
    main()
