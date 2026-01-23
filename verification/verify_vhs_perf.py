from playwright.sync_api import sync_playwright, expect
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock the API calls
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"output": "SYSTEM ONLINE. VHS CHECK.", "state": {"sanity": 100, "reality": 100, "location": "TEST", "time": "08:00", "day": "14", "mental_load": 50, "attention_level": 50}}'
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=30000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return

        print("Page loaded")

        # Wait for Title Screen and Start
        start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
        try:
            start_btn.wait_for(timeout=10000)
            start_btn.click()
        except:
            print("Start button not found.")
            page.screenshot(path="verification/vhs_debug_fail.png")
            return

        # Wait for VHS container
        vhs_container = page.locator(".vhs-container")
        vhs_container.wait_for(timeout=10000)
        print("VHS Container found")

        # Check Tape Counter (it should change if re-rendering/updating)
        counter = page.locator(".tape-counter")
        counter.wait_for(timeout=5000)

        initial_text = counter.text_content()
        print(f"Initial counter: {initial_text}")

        time.sleep(0.5)

        next_text = counter.text_content()
        print(f"Next counter: {next_text}")

        # Check Glitch Overlay Transform
        glitch = page.locator(".glitch-overlay")

        initial_transform = glitch.evaluate("el => getComputedStyle(el).transform")
        print(f"Initial transform: {initial_transform}")

        time.sleep(0.5)

        next_transform = glitch.evaluate("el => getComputedStyle(el).transform")
        print(f"Next transform: {next_transform}")

        if initial_text != next_text:
            print("Counter changed (Animation active)")
        else:
            print("Counter did not change (Animation potentially stuck or slow)")

        if initial_transform != next_transform:
            print("Transform changed (Animation active)")
        else:
            print("Transform did not change (Animation potentially stuck)")

        page.screenshot(path="verification/vhs_optimization.png")
        print("Screenshot saved to verification/vhs_optimization.png")

        browser.close()

if __name__ == "__main__":
    run()
