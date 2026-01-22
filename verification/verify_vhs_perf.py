from playwright.sync_api import sync_playwright, expect
import time
import os
import json

def run():
    print("Starting VHS Effect Performance Verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock API to return high mental load to trigger effects
        mock_state = {
            "output": "SYSTEM ONLINE.",
            "state": {
                "sanity": 50,
                "reality": 50,
                "mental_load": 80,
                "attention_level": 60,
                "psych_flags": {
                    "disorientation": False,
                    "instability": True
                },
                "location": "TEST",
                "time": "00:00",
                "day": "1"
            }
        }

        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_state)
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=60000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return

        # Start game
        try:
            start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
            start_btn.wait_for(timeout=10000)
            start_btn.click()
            print("Started game...")
        except Exception as e:
            print(f"Failed to start game: {e}")
            page.screenshot(path="verification/vhs_error.png")
            return

        # Wait for VHS container
        vhs = page.locator(".vhs-container")
        vhs.wait_for(timeout=10000)
        print("VHS Container found.")

        # Check .glitch-overlay style updates
        glitch = page.locator(".glitch-overlay")
        noise = page.locator(".static-noise")

        # Sample styles
        samples_glitch = []
        samples_noise = []

        print("Sampling animation styles...")
        for i in range(5):
            style_g = glitch.get_attribute("style")
            style_n = noise.get_attribute("style")
            samples_glitch.append(style_g)
            samples_noise.append(style_n)
            time.sleep(0.1)

        # Verify changes
        unique_glitch = set(samples_glitch)
        unique_noise = set(samples_noise)

        print(f"Unique glitch styles captured: {len(unique_glitch)}/5")
        print(f"Unique noise styles captured: {len(unique_noise)}/5")

        if len(unique_glitch) > 1 and len(unique_noise) > 1:
            print("SUCCESS: Animation is running (styles are updating).")
            page.screenshot(path="verification/vhs_success.png")
        else:
            print("FAILURE: Animation appears frozen.")
            print("Glitch samples:", samples_glitch)
            print("Noise samples:", samples_noise)
            exit(1)

        browser.close()

if __name__ == "__main__":
    run()
