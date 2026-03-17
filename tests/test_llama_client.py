"""Regression tests for llama-server request shaping."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from config import LLAMA_MAX_TOKENS, LLAMA_TEMPERATURE, LLAMA_TOP_P
from llama_client import LlamaChatClient


class LlamaChatClientTests(unittest.TestCase):
    """Verify compact generation defaults are sent to llama-server."""

    @patch("llama_client.requests.post")
    def test_chat_sends_compact_generation_settings(self, mock_post: Mock) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": " Short reply. "}}]
        }
        mock_post.return_value = mock_response

        client = LlamaChatClient(base_url="http://127.0.0.1:8080")
        result = client.chat("System prompt", "User prompt")

        self.assertEqual("Short reply.", result)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["max_tokens"], LLAMA_MAX_TOKENS)
        self.assertEqual(payload["temperature"], LLAMA_TEMPERATURE)
        self.assertEqual(payload["top_p"], LLAMA_TOP_P)
        self.assertEqual(payload["reasoning_format"], "none")
        self.assertEqual(payload["chat_template_kwargs"], {"enable_thinking": False})


if __name__ == "__main__":
    unittest.main()
