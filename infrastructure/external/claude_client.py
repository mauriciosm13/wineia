from anthropic import Anthropic
from core.utils.load_config import load_config

class ClaudeClient:

    def generate(self, system_prompt, user_prompt):
        config = load_config()
        api_key = config["ANTHROPIC_API_KEY"]
        model = config["ANTHROPIC_API_MODEL"]

        client = Anthropic(api_key=api_key)

        message = client.messages.create(
                model=model,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{user_prompt}"
                        ),
                    }
                ],
            )

        contents = message.content
        if not contents:
            return ""

        contents = getattr(message, "content", None) or []
        for item in contents:
            if getattr(item, "type", None) == "text" and hasattr(item, "text"):
                return item.text or ""

        return ""
