## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-23 - [Path Traversal in Export Logic]
**Vulnerability:** `SaveSystem.export_save` accepted an arbitrary path from user input (via `debugexport` command), allowing files to be written anywhere the process had access (Path Traversal/Arbitrary File Write).
**Learning:** Functions intended for "exporting" data often default to assuming the path is safe or just a filename, but when exposed via CLI or API, they become vectors for file system attacks. Even "debug" commands are attack surfaces if not strictly gated.
**Prevention:** Always treat file paths as untrusted input. Use `os.path.basename()` to strip directory components and strictly join with a trusted base directory. Use `os.path.abspath()` and `startswith()` checks for extra safety if subdirectories are needed.
