## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** `server.py` exposed a `/api/shutdown` endpoint that allowed unauthenticated users to terminate the server process.
**Learning:** Convenience features for local testing (like remote shutdown) can become critical denial-of-service vulnerabilities if left in production-capable code, especially when binding to `0.0.0.0`.
**Prevention:** Remove debug/control endpoints from production code paths or gate them behind strict authentication and environment flags.
