"""Opt-in Ollama local chat connector with localhost-only target validation."""
from __future__ import annotations
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen
class OllamaConnector:
    name = "ollama"
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 20.0):
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}: raise ValueError("Ollama connector only accepts an explicit localhost HTTP endpoint")
        if not model or not model.strip(): raise ValueError("Ollama model is required")
        if not 1 <= timeout_seconds <= 120: raise ValueError("timeout_seconds must be between 1 and 120")
        self.endpoint, self.model, self.timeout_seconds = base_url.rstrip("/") + "/api/chat", model.strip(), timeout_seconds
    def healthcheck(self): return {"name": self.name, "enabled": True, "model": self.model, "endpoint": self.endpoint}
    def chat(self, messages: list[dict[str, str]]) -> str:
        if not isinstance(messages, list) or not messages: raise ValueError("messages must be a non-empty list")
        for message in messages:
            if not isinstance(message, dict) or message.get("role") not in {"system", "user", "assistant"} or not isinstance(message.get("content"), str): raise ValueError("each message needs a valid role and text content")
        body = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode()
        request = Request(self.endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout_seconds) as response: result = json.loads(response.read(2_000_000).decode("utf-8"))
        content = result.get("message", {}).get("content")
        if not isinstance(content, str): raise RuntimeError("Ollama returned no message content")
        return content
