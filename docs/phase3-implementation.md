# Phase 3 — bots, persistence and connectors

## Bot families added

- ALPHA: intake validation, task planning and artifact QA. The worker produces an explicit work plan and returns `NEEDS_ADAPTER` until an authorized execution/delivery adapter is configured.
- BETA: ranks supplied opportunity candidates, qualifies leads only when contact permission is explicitly true, and reconciles expected versus received commission amounts. It does not scrape sites, send unsolicited messages or place orders.
- GAMMA: validates market-data fields, checks portfolio exposure against a supplied limit, and prepares traditional-asset research. Crypto is rejected and no investment order can be emitted.

## Runtime wiring

`core/worker_registry.py` exposes `build_orchestrator()`, which registers the three phase-three bot workers for the existing runtime/scheduler. Existing `core/store.py`, `core/runtime.py` and `core/scheduler.py` are not replaced by this phase.

## Connectors

- Ollama: opt-in local HTTP chat adapter, localhost-only, bounded timeout. No remote host is accepted.
- Marketplaces: disabled adapter; requires provider-specific official API, account scopes and terms review.
- Payments: generic HMAC-SHA256 verifier and idempotent inbound-receipt ledger. This is not a Stripe/Bizum/SEPA integration: each provider needs its own signature canonicalization, webhook endpoint, event mapping and reconciliation tests.

## Security boundary

No connector can initiate a transfer, payout, refund, subscription, purchase or broker order. Payment receipts remain `PENDING_RECONCILIATION` until a separate verified reconciliation process is implemented. Never put secrets in Git.

## Verification

Run `python -m unittest discover -s tests -v`. External provider calls are deliberately not part of unit tests; use provider sandbox accounts and signed test webhooks before any production activation.
