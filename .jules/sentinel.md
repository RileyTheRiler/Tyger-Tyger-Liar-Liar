## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` ('tyger_tyger_secret') in `web/server.py`.
**Learning:** Hardcoded secrets in source control are a persistent risk, even in local-first apps, as they can be blindly copied into production.
**Prevention:** Always use environment variables or random generation for secrets. Added `secrets.token_hex(32)` as a secure fallback.

## 2024-06-11 - Critical Syntax Error in Scene Manager
**Vulnerability:** A duplicate `__init__` definition in `src/engine/scene_manager.py` caused a syntax error, preventing the server from starting. While not a direct exploit, it represents a denial of service (DoS) state where the application cannot function.
**Learning:** Automated tools or copy-paste errors can easily introduce syntax errors that bypass cursory checks if linting/testing isn't enforced before deployment. The previous change seems to have duplicated the constructor signature without merging the body.
**Prevention:** Fix the syntax error by merging the constructors. Enforce `pnpm lint` and local testing before commitment.
