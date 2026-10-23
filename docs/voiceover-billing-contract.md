# Voiceover billing implementation contract (not yet enabled)

The proposed Multilingual v2 price is **3 Channel Coach credits per 1,000
characters, rounded up per generated section**. Existing package: 75 credits
for $6.99. This is a proposed product price, not a verified cost guarantee.

## Before any commercial generation

- Upgrade ElevenLabs from Free to a plan permitting commercial use.
- Confirm API character accounting and model-specific provider costs.
- Verify authenticated Supabase session on the server; never accept a
  user-supplied ID as proof of authentication.
- Review and apply the draft job migration only after checking the live
  Supabase schema and policies.
- Implement a **single PostgreSQL transaction** to create a unique job
  (user_id, request_key), revalidate the quote, and reserve/deduct credits
  using the existing ledger. A separate application-level job insert and
  spend_credits() call is **not atomic** and is forbidden.
- A repeated request_key must return the existing job state and never spend
  again. Bind request_key to the same text hash, voice, model and price;
  reject attempts to reuse it for different content.
- Implement durable worker claims/leases and provider-call uncertainty
  handling. On timeout, do not assume failure or retry blindly.
- Store MP3s in private per-user Supabase Storage; issue short-lived
  authenticated download links and verify ownership on every access.
- Add an idempotent compensating refund transaction only for confirmed
  non-delivery. Never issue an unconditional refund on provider timeout.
- Implement per-user quotas, max characters, bounded concurrency, and
  request-rate limits.
- End-to-end test simultaneous requests, retries, failed storage writes,
  provider failures, insufficient balance, and charge/refund reconciliation.
- Do not enable the UI generation action until all tests pass and a human
  reviews the release.

## Current state

Only script editing, voice listing, non-billable quoting, quote confirmation,
read-only job history helper, and a fail-closed generation guard exist on
this development branch. No live database migration, credit reservation,
ElevenLabs generation, or commercial rollout has been performed.
