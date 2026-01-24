from playwright.sync_api import sync_playwright, expect
import time
import os
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock the API calls to trigger VHS effects (mental_load > 0)
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "output": "SYSTEM ONLINE.",
                "state": {
                    "sanity": 100,
                    "reality": 100,
                    "location": "HQ",
                    "time": "08:00",
                    "day": "14",
                    "mental_load": 50,
                    "attention_level": 50,
                    "psych_flags": {
                        "disorientation": False,
                        "instability": False
                    }
                }
            })
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=60000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return

        # Start game
        start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
        try:
            start_btn.wait_for(timeout=10000)
            start_btn.click()
        except:
            print("Start button failed.")
            page.screenshot(path="verification/vhs_fail_start.png")
            browser.close()
            return

        # Wait for VHS container
        vhs = page.locator(".vhs-container")
        try:
            vhs.wait_for(state="visible", timeout=10000)
        except:
             print("VHS container not found.")
             page.screenshot(path="verification/vhs_fail_container.png")
             browser.close()
             return

        print("VHS container found. monitoring styles...")

        glitch = page.locator(".glitch-overlay")

        styles = []
        for i in range(10):
            style = glitch.get_attribute("style")
            print(f"Sample {i}: {style}")
            styles.append(style)
            time.sleep(0.1)

        # Verify styles changed
        unique_styles = set(styles)
        if len(unique_styles) > 1:
            print("SUCCESS: Styles are changing (Animation is active).")
            page.screenshot(path="verification/vhs_optimization.png")
        else:
            print("FAILURE: Styles are static.")
            page.screenshot(path="verification/vhs_fail_static.png")
            browser.close()
            exit(1)

        browser.close()

if __name__ == "__main__":
    run()
