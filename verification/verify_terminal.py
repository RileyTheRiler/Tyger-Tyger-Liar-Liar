from playwright.sync_api import sync_playwright, expect
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with reduced motion to minimize animation flakiness, though framer-motion might ignore it depending on config
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock the API calls to avoid backend dependency
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"output": "SYSTEM ONLINE. WELCOME AGENT.", "state": {"sanity": 100, "reality": 100, "location": "HQ", "time": "08:00", "day": "14"}}'
        ))

        # Navigate to the app
        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=60000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            # Try to read the vite log
            if os.path.exists("/tmp/vite.log"):
                with open("/tmp/vite.log", "r") as f:
                    print(f.read())
            return

        print("Page loaded")

        # Wait for Title Screen
        # The title screen has a [START_INVESTIGATION] button.
        start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")

        print("Waiting for start button...")
        try:
            start_btn.wait_for(timeout=10000)
        except:
             print("Start button not found. Dumping content:")
             # print(page.content())
             page.screenshot(path="verification/debug_title_fail.png")
             browser.close()
             return

        print("Clicking start button...")
        start_btn.click()

        # Wait for Terminal to appear.
        # The terminal has class "terminal-window"
        terminal = page.locator(".terminal-window")
        terminal.wait_for(timeout=10000)

        # Verify text appears (Mocked response)
        expect(page.get_by_text("SYSTEM ONLINE")).to_be_visible()

        # Take screenshot
        print("Taking screenshot...")
        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/terminal_optimization.png")

        print("Verification complete.")
        browser.close()

if __name__ == "__main__":
    run()
