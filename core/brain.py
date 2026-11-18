"""Bounded chat-completion adapter for local Ollama or explicitly enabled remote APIs."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str | None
    endpoint: str | None
    api_key_env: str | None

PROVIDERS = {
    "openai": ("OPENAI_MODEL", "OPENAI_BASE_URL", "OPENAI_API_KEY"),
    "xai": ("XAI_MODEL", "XAI_BASE_URL", "XAI_API_KEY"),
    "ollama": ("OLLAMA_MODEL", "OLLAMA_BASE_URL", None),
    "pollinations": ("POLLINATIONS_MODEL", "POLLINATIONS_BASE_URL", "POLLINATIONS_API_KEY"),
}

def provider_config(name: str | None = None) -> ProviderConfig:
    selected = (name or os.getenv("AI_PROVIDER", "ollama")).strip().lower()
    if selected not in PROVIDERS:
        raise ValueError(f"Unsupported AI provider: {selected}")
    model_env, endpoint_env, key_env = PROVIDERS[selected]
    return ProviderConfig(selected, os.getenv(model_env), os.getenv(endpoint_env), key_env)

def chat(messages: list[dict[str, str]], provider: str | None = None,
         timeout_seconds: int = 30, max_tokens: int = 1024) -> str:
    """Call a configured model. Remote providers require explicit AI_REMOTE_ENABLED=1."""
    if not isinstance(messages, list) or not messages or len(messages) > 40:
        raise ValueError("messages must contain between 1 and 40 entries")
    if any(not isinstance(m, dict) or m.get("role") not in {"system", "user", "assistant"}
           or not isinstance(m.get("content"), str) for m in messages):
        raise ValueError("Each message requires a supported role and string content")
    if sum(len(m["content"]) for m in messages) > 100_000:
        raise ValueError("Prompt exceeds the 100k-character safety limit")
    if not 1 <= timeout_seconds <= 90 or not 1 <= max_tokens <= 2048:
        raise ValueError("timeout_seconds must be 1..90 and max_tokens 1..2048")

    cfg = provider_config(provider)
    if not cfg.model:
        raise RuntimeError(f"Model is not configured for provider: {cfg.name}")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if cfg.name == "ollama":
        base = (cfg.endpoint or "http://localhost:11434").rstrip("/")
        parsed = urlparse(base)
        if (parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
                or parsed.username or parsed.password):
            raise PermissionError("Ollama is restricted to an explicit localhost HTTP endpoint")
        url = base if base.endswith("/api/chat") else base + "/api/chat"
        body = {"model": cfg.model, "messages": messages, "stream": False,
                "options": {"num_predict": max_tokens}}
    else:
        if os.getenv("AI_REMOTE_ENABLED", "0") != "1":
            raise PermissionError("Remote AI is disabled; set AI_REMOTE_ENABLED=1 explicitly")
        if not cfg.endpoint:
            raise RuntimeError(f"Endpoint is not configured for provider: {cfg.name}")
        if not cfg.api_key_env:
            raise RuntimeError("Remote provider has no configured API-key variable")
        api_key = os.getenv(cfg.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing credential in environment variable: {cfg.api_key_env}")
        base = cfg.endpoint.rstrip("/")
        url = base if base.endswith("/chat/completions") else base + "/chat/completions"
        headers["Authorization"] = "Bearer " + api_key
        body = {"model": cfg.model, "messages": messages, "stream": False,
                "max_tokens": max_tokens}

    request = Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"AI provider returned HTTP {response.status}")
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise RuntimeError("AI provider response exceeded 2 MB")
    except HTTPError as exc:
        raise RuntimeError(f"AI provider returned HTTP {exc.code}") from None
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"AI provider connection failed: {type(exc).__name__}") from None

    try:
        data = json.loads(raw.decode("utf-8"))
        content = (data["message"]["content"] if cfg.name == "ollama"
                   else data["choices"][0]["message"]["content"])
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        raise RuntimeError("AI provider returned an invalid response schema") from None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("AI provider returned empty content")
    return content.strip()
