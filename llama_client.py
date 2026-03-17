"""Small OpenAI-style client for llama-server chat completions."""

from __future__ import annotations

from pathlib import Path

import requests

from config import (
    LLAMA_BASE_URL,
    LLAMA_MAX_TOKENS,
    LLAMA_TEMPERATURE,
    LLAMA_TOP_P,
    NEMOTRON_MODEL,
)


class LlamaChatClient:
    """Send simple system+user chat requests to llama-server."""

    def __init__(self, base_url: str = LLAMA_BASE_URL, timeout: int = 90) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.model_name = Path(NEMOTRON_MODEL).name if NEMOTRON_MODEL else "local-model"

    def chat(self, system_prompt: str, user_message: str) -> str:
        """Return choices[0].message.content from chat completions."""
        payload = {
            "model": self.model_name,
            "max_tokens": LLAMA_MAX_TOKENS,
            "temperature": LLAMA_TEMPERATURE,
            "top_p": LLAMA_TOP_P,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Unexpected llama-server response format") from exc

        return content.strip()
