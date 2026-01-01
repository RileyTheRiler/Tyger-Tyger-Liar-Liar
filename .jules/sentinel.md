## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-25 - Unauthenticated Shutdown Endpoint
**Vulnerability:** Re-discovered `/api/shutdown` in `server.py` which allowed unauthenticated remote termination of the server process via `os.kill`.
**Learning:** Features intended for local development convenience (like remote shutdown) can persist into production-like environments if not strictly guarded or removed. Regression occurred where a previous fix was seemingly reverted or applied to a different file.
**Prevention:** Removed the endpoint entirely. Dangerous administrative actions must be authenticated or restricted to local signals only. Added regression test `tests/test_server_security.py`.
