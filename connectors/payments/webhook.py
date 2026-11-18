"""Generic HMAC verifier; provider-specific canonicalization must be implemented separately."""
import hashlib
import hmac
class InvalidWebhookSignature(ValueError): pass
def verify_hmac_sha256(raw_body: bytes, signature: str, secret: str) -> bool:
    if not isinstance(raw_body, bytes) or not secret: raise ValueError("raw_body bytes and webhook secret are required")
    supplied = signature.removeprefix("sha256=").strip().lower()
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, supplied): raise InvalidWebhookSignature("Webhook signature is invalid")
    return True
