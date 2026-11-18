# Phase 3 — bots, persistence and connectors

## Bot families added

- ALPHA: validates intake, creates a task plan and performs basic artifact QA. It returns NEEDS_ADAPTER until an authorized execution/delivery adapter is configured.
- BETA: ranks supplied opportunity candidates, qualifies leads only when contact permission is explicitly true, and reconciles expected versus received commission amounts using integer minor units. It does not scrape sites, send messages or place orders.
- GAMMA: validates market-data structure, performs explicit exposure checks only when risk inputs are supplied, and prepares traditional-asset research. Missing risk inputs are reported as NOT_EVALUATED, not as a pass. Data freshness is not yet verified. Crypto is rejected and no investment order can be emitted.

## Runtime wiring

core/worker_registry.py registers the three phase-three bot workers. core/app.py now uses this registry when building the persistent runtime. core/store.py provides the SQLite queue, idempotency, audit events, leases and recovery after an expired worker lease. core/scheduler.py starts only through the explicit run_worker.py entry point.

## Connectors

- Ollama: opt-in local HTTP chat adapter, localhost-only, bounded timeout and response size.
- Marketplaces: disabled adapter; requires provider-specific official API, account scopes, terms review, sandbox and attribution proof.
- Payments: generic HMAC-SHA256 helper and idempotent inbound-receipt ledger. The ledger method accepts events that the caller has already verified; it does not verify provider signatures itself. This is not a Stripe/Bizum/SEPA integration. Each provider still needs its own signature canonicalization, replay protection, webhook endpoint, event mapping and reconciliation tests.
- Banking: read-only banking connection and transaction reconciliation are not implemented.
- Broker: no broker connection exists. GAMMA remains research-only.

## Security boundary

No connector can initiate a transfer, payout, refund, subscription, purchase or broker order. Payment receipts remain PENDING_RECONCILIATION until a separate verified reconciliation process is implemented. Never put secrets, raw webhook bodies or unnecessary personal data in Git or ledger metadata.

## Verification

Run python -m unittest discover -s tests -v. CI runs Python 3.11 compile and unit tests. External provider calls are deliberately excluded from unit tests; use provider sandbox accounts and signed test webhooks before any production activation.
