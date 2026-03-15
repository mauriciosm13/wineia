import os
import requests


class ClaudeClient:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
        self.base_url = "https://api.anthropic.com/v1/messages"

    def generate(self, system_prompt, user_prompt):
        """
        Call Anthropic Claude API to generate a text response.
        """
        if not self.api_key:
            raise RuntimeError("CLAUDE_API_KEY is not set")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": 512,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
        }

        response = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        contents = data.get("content", [])
        if not contents:
            return ""

        for item in contents:
            if item.get("type") == "text":
                return item.get("text", "")

        return ""
