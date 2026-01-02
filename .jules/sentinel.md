## 2024-03-24 - [CRITICAL] Unauthenticated Remote Shutdown Endpoint
**Vulnerability:** The `server.py` file exposed a `/api/shutdown` endpoint that allowed unauthenticated users to terminate the server process via `os.kill`.
**Learning:** Development convenience features (like remote shutdown for testing) can easily leak into production if not strictly guarded or removed. The presence of tests verifying this "feature" (`tests/test_shutdown.py`) normalized its existence.
**Prevention:**
1. Never expose process control endpoints in production builds.
2. If required for testing, guard them with `if os.environ.get("TEST_MODE"):` checks or separate them into a test-only router.
3. Security tests should verify the *absence* of such endpoints in production configuration, not their functionality.
