"""Opt-in Ollama local chat connector restricted to localhost."""
from __future__ import annotations
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen

class OllamaConnector:
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 20.0):
        parsed = urlparse(base_url)
        if (parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
                or parsed.username or parsed.password):
            raise ValueError("Ollama connector only accepts an explicit localhost HTTP endpoint")
        if not model or not model.strip():
            raise ValueError("Ollama model is required")
        if not 1 <= timeout_seconds <= 120:
            raise ValueError("timeout_seconds must be between 1 and 120")
        base = base_url.rstrip("/")
        self.endpoint = base if base.endswith("/api/chat") else base + "/api/chat"
        self.model = model.strip()
        self.timeout_seconds = timeout_seconds

    def healthcheck(self):
        return {"name": self.name, "enabled": True, "model": self.model,
                "endpoint": self.endpoint}

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not isinstance(messages, list) or not messages or len(messages) > 40:
            raise ValueError("messages must contain between 1 and 40 entries")
        total = 0
        for message in messages:
            if (not isinstance(message, dict) or
                    message.get("role") not in {"system", "user", "assistant"} or
                    not isinstance(message.get("content"), str)):
                raise ValueError("each message needs a valid role and text content")
            total += len(message["content"])
        if total > 100_000:
            raise ValueError("prompt exceeds 100k characters")
        body = json.dumps({"model": self.model, "messages": messages,
                           "stream": False}).encode("utf-8")
        request = Request(self.endpoint, data=body,
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise RuntimeError("Ollama response exceeded 2 MB")
        try:
            result = json.loads(raw.decode("utf-8"))
            content = result["message"]["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError):
            raise RuntimeError("Ollama returned an invalid response schema") from None
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama returned empty content")
        return content.strip()
