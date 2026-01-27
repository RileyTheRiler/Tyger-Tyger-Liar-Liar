## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2026-01-27 - Arbitrary File Write in Debug Commands
**Vulnerability:** The `debugexport` command allowed users to specify an absolute path for exporting save files, leading to arbitrary file write/overwrite capabilities.
**Learning:** Debug tools and console commands often bypass standard validation layers. Even "internal" tools must assume hostile input, especially if they interact with the file system.
**Prevention:** Enforced a dedicated export directory and sanitized filenames using `os.path.basename` to prevent path traversal.
