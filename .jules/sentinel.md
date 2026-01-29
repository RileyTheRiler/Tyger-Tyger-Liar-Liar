## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `/api/shutdown` endpoint in `server.py` allowed unauthenticated termination of the server process via a simple POST request.
**Learning:** Convenience features for local development (like a remote shutdown button) can become critical DoS vulnerabilities if the application is deployed or exposed on a network interface (0.0.0.0).
**Prevention:** Removed the endpoint entirely. Server lifecycle should be managed by the infrastructure (systemd, Docker, user), not the application itself.

## 2024-05-25 - Path Traversal in Export Function
**Vulnerability:** `SaveSystem.export_save` accepted an arbitrary file path, allowing writing to any location the process had access to (Arbitrary File Write).
**Learning:** Functions intended for "exporting" data must not trust user-provided paths. Even if the feature is behind a debug flag, it can be chained with other exploits or enabled by attackers if authentication is weak.
**Prevention:** Enforce a dedicated export directory. Treat user input as a filename only (sanitize with `os.path.basename`) and construct the path serverside.
