## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2025-01-26 - Arbitrary File Write via Debug Export
**Vulnerability:** The `debugexport` command in `game.py` allowed path traversal in the filename argument, enabling arbitrary file writes on the server via the `/api/action` endpoint.
**Learning:** Debug features exposed in production/networked environments are high-risk entry points. Input validation must occur at the sink (`SaveSystem`), not just the source (CLI/API).
**Prevention:** Restricted file writes to a dedicated `exports/` directory using `os.path.basename` and enforced output path sanitization.
