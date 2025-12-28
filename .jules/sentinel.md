## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-05-24 - Insecure Flask Defaults
**Vulnerability:** `web/server.py` was configured with `debug=True`, `allow_unsafe_werkzeug=True`, and `host='0.0.0.0'`. This exposed the Werkzeug debugger (allowing arbitrary code execution) to the entire network.
**Learning:** Local dev tools often get committed with "convenience" defaults that are catastrophic if run on a public network or production-like environment.
**Prevention:** Always default to `127.0.0.1` and `debug=False`. Use environment variables (`FLASK_DEBUG`, `HOST`) to opt-in to unsafe behaviors for development only.
