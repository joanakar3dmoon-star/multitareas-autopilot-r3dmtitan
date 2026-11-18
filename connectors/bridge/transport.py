"""Small HTTPS-only JSON transport with redirects disabled."""
from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def validate_base_url(value: str) -> str:
    parsed = urlparse(value)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (local and parsed.scheme == "http"):
        raise ValueError("bridge endpoint must use HTTPS (HTTP is allowed only on localhost)")
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("invalid bridge base URL")
    return value.rstrip("/")

def validate_path(path: str) -> str:
    parsed = urlparse(path)
    if (not isinstance(path, str) or not path.startswith("/") or ".." in path.split("/")
            or parsed.scheme or parsed.netloc or parsed.query or parsed.fragment):
        raise ValueError("bridge path must be an absolute safe path without query or fragment")
    return path

def request_json(url: str, method: str = "GET", payload: dict | None = None,
                 headers: dict[str, str] | None = None, timeout: int = 10) -> dict:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8") if payload is not None else None
    request = Request(url, data=data, headers=headers or {}, method=method)
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise RuntimeError("bridge response exceeded 1 MB")
            if not raw:
                return {"ok": True}
            result = json.loads(raw.decode("utf-8"))
            return result if isinstance(result, dict) else {"data": result}
    except HTTPError as exc:
        raise RuntimeError(f"bridge returned HTTP {exc.code}") from None
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"bridge transport failed: {type(exc).__name__}") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("bridge returned invalid JSON") from None
