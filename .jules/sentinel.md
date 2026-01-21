## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Path Traversal in Export Functionality
**Vulnerability:** The `SaveSystem.export_save` method accepted an arbitrary file path, allowing path traversal (e.g., `../../file`) and arbitrary file writes outside the intended directory.
**Learning:** Functions intended for "exporting" data often default to accepting full paths for flexibility, but this creates a security gap when exposed to user input (e.g., via debug consoles or APIs).
**Prevention:** Enforce a strict "filename only" policy for exports and confine them to a specific directory (e.g., `exports/`). Validate filenames against an allowlist (alphanumeric, dots, etc.) and explicitly reject traversal characters (`..`).
