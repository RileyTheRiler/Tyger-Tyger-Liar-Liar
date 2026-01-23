## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Arbitrary File Write in Save System
**Vulnerability:** The `SaveSystem.export_save` method accepted an arbitrary `output_path` and wrote the save file there, allowing a user to overwrite any file on the server (e.g., source code, configs) via the `debugexport` command which is accessible by toggling `debug` mode.
**Learning:** Functions that write to files based on user input must effectively isolate the writing to a safe directory, even if they are intended for debugging tools. Debug tools often become attack vectors if exposed.
**Prevention:** Updated `SaveSystem` to require an `export_directory` and changed `export_save` to accept only a filename, enforcing a strict allowlist of characters and canonicalizing the path to prevent traversal. Also fixed a double-JSON-dump bug that masked the issue.
