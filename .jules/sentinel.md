## 2024-05-23 - Unauthenticated Shutdown Endpoint
**Vulnerability:** The `server.py` file exposed a POST endpoint `/api/shutdown` that triggered `os.kill` on the server process. This endpoint was unauthenticated and bound to 0.0.0.0, allowing anyone with network access to shut down the game server (DoS).
**Learning:** Development convenience features (like remote shutdown) often slip into production candidates if not explicitly gated by debug flags or removed. Python web frameworks make it very easy to add these "god mode" endpoints.
**Prevention:**
1. Never expose process control endpoints in production builds.
2. If needed for local dev, wrap them in `if app.debug:` or similar checks, or require a secret token header.
3. Use process managers (systemd, docker, supervisor) to handle shutdowns, rather than application logic.
