from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock API calls
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"output": "SYSTEM ONLINE", "state": {"mental_load": 50, "attention": 50, "instability": false, "disorientation": false}}'
        ))

        print("Navigating...")
        page.goto("http://localhost:5173")

        # Start game
        print("Clicking Start...")
        page.click("button:has-text('[START_INVESTIGATION]')")

        # Wait for VHSEffect to appear.
        print("Waiting for VHS container...")
        page.wait_for_selector(".vhs-container.active", timeout=15000)

        # Wait a bit for animation
        time.sleep(1)

        # Get initial tape counter text
        counter = page.locator(".tape-counter")
        text1 = counter.inner_text()
        print(f"Counter 1: {text1}")

        time.sleep(0.2) # 200ms
        text2 = counter.inner_text()
        print(f"Counter 2: {text2}")

        if text1 == text2:
            print("WARNING: Counter did not change! Animation loop might be broken.")
        else:
            print("SUCCESS: Counter is updating.")

        # Screenshot
        page.screenshot(path="verification/vhs_opt.png")
        print("Screenshot saved to verification/vhs_opt.png")

        browser.close()

if __name__ == "__main__":
    run()
