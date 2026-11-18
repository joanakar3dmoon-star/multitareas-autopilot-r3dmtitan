import json
import os
import unittest
from unittest.mock import patch

from core.brain import chat, provider_config


class FakeResponse:
    status = 200
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        return False
    def read(self, _limit):
        return self.payload


class BrainTests(unittest.TestCase):
    @patch.dict(os.environ, {"AI_PROVIDER": "ollama", "OLLAMA_MODEL": "local-model",
                             "OLLAMA_BASE_URL": "http://localhost:11434"}, clear=True)
    @patch("core.brain.urlopen")
    def test_ollama_chat_uses_local_endpoint(self, mocked):
        mocked.return_value = FakeResponse({"message": {"content": " listo "}})
        result = chat([{"role": "user", "content": "hola"}])
        self.assertEqual(result, "listo")
        self.assertEqual(mocked.call_args.args[0].full_url,
                         "http://localhost:11434/api/chat")

    @patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_MODEL": "m",
                             "OPENAI_BASE_URL": "https://example.invalid/v1",
                             "OPENAI_API_KEY": "test-secret", "AI_REMOTE_ENABLED": "0"}, clear=True)
    def test_remote_provider_requires_explicit_opt_in(self):
        with self.assertRaises(PermissionError):
            chat([{"role": "user", "content": "hello"}])

    def test_unknown_provider_rejected(self):
        with self.assertRaises(ValueError):
            provider_config("not-a-provider")

    def test_prompt_size_is_bounded(self):
        with self.assertRaises(ValueError):
            chat([{"role": "user", "content": "x" * 100_001}])


if __name__ == "__main__":
    unittest.main()
