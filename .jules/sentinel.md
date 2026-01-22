## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Path Traversal in Save Export
**Vulnerability:** `SaveSystem.export_save` accepted an arbitrary `output_path`, allowing users (via `debugexport` command) to overwrite any file the process had access to.
**Learning:** Functions intended for "exporting" data must enforce destination boundaries, especially when exposed to user input (even if behind a debug flag). Validating "slots" isn't enough if "filenames" are also accepted.
**Prevention:** Added `_validate_filename` to prevent path traversal (`..`, `/`) and restricted exports to a dedicated `exports/` directory.
