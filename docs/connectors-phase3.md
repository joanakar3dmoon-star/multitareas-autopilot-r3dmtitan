# Phase 3 connector contracts

| Connector | Status | Activation requirement |
|---|---|---|
| Ollama local AI | Executable, opt-in | Local model running; explicit localhost URL and model; timeout configured |
| Marketplace / affiliate | Disabled by default | Provider-specific official API, OAuth scopes, terms approval, sandbox and attribution proof |
| Payment webhook | Generic signature helper only | Provider-specific signature scheme, timestamp/replay defence, endpoint authentication and sandbox test |
| Inbound receipt ledger | Executable local ledger | Verified provider event mapped to immutable event ID, minor-unit amount and currency; reconciliation still pending |
| Bank reconciliation | Not implemented | Authorized read-only banking API, consent, scopes, webhook/polling, transaction matching and audit |
| Broker | Not implemented | Authorized broker API, risk limits, instrument allowlist, human approval and kill switch; GAMMA stays research-only |

A generic HMAC helper is not proof of compatibility with a provider's production webhook format. A connector health check is not proof of account authorization or production readiness.
