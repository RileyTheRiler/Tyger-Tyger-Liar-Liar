## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Overly Permissive CORS Configuration
**Vulnerability:** `web/server.py` was configured with `cors_allowed_origins='*'`, allowing any website to connect to the WebSocket server.
**Learning:** Using wildcard CORS (`*`) for convenience during development exposes the application to Cross-Site WebSocket Hijacking (CSWSH) and CSRF-like attacks in production.
**Prevention:** Restrict CORS to specific trusted origins (e.g., localhost during dev). Implemented an environment variable `CORS_ALLOWED_ORIGINS` to allow configuration while defaulting to safe local ports.
