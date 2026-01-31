from playwright.sync_api import sync_playwright, expect
import time
import os
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock the API calls
        mock_response = {
            "output": "SYSTEM ONLINE.",
            "state": {
                "mental_load": 50, # Sufficient load to trigger effects
                "psych_flags": {"disorientation": False, "instability": False},
                "music": "ambient.mp3"
            }
        }

        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        ))

        print("Navigating to http://localhost:5173")
        try:
            page.goto("http://localhost:5173", timeout=30000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return

        # Start game
        try:
            start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
            start_btn.wait_for(timeout=10000)
            start_btn.click()
        except:
            print("Start button failed")
            page.screenshot(path="verification/vhs_fail_start.png")
            browser.close()
            return

        # Wait for VHSEffect components
        glitch = page.locator(".glitch-overlay")
        counter = page.locator(".tape-counter")

        try:
            glitch.wait_for(timeout=10000)
            counter.wait_for(timeout=10000)
        except:
            print("VHSEffect elements not found")
            page.screenshot(path="verification/vhs_fail_load.png")
            browser.close()
            return

        print("Checking for animation updates...")

        # Get initial style
        initial_style = glitch.get_attribute("style")
        time.sleep(0.5)
        new_style = glitch.get_attribute("style")

        if initial_style != new_style:
            print("SUCCESS: Glitch overlay style is updating.")
        else:
            print("FAILURE: Glitch overlay style is static.")

        print(f"Initial: {initial_style}")
        print(f"Current: {new_style}")

        # Check counter presence
        print(f"Counter text: {counter.text_content()}")

        page.screenshot(path="verification/vhs_verification.png")
        browser.close()

if __name__ == "__main__":
    run()
