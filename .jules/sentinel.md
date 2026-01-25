## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Path Traversal in Save Export
**Vulnerability:** The `export_save` function in `src/engine/save_system.py` allowed writing files to arbitrary paths via the `output_path` argument (e.g., `../pwned.txt`). This was exposed via the `debugexport` command in `game.py`.
**Learning:** Functions that accept file paths as arguments from user input (even indirectly via debug commands) must explicitly validate or sanitize them, as they can bypass intended directory restrictions.
**Prevention:** Used `os.path.basename` to strip directory components and enforced writing to a strictly defined `export_directory`.
