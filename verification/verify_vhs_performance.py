from playwright.sync_api import sync_playwright, expect
import time
import os
import subprocess
import sys

def run():
    print("Starting verification for VHSEffect performance...")

    # Ensure server is running (check port 5173)
    # This is a basic check; if not running, we assume the environment might be set up elsewhere
    # or we might fail navigation. Ideally we'd start it, but "do not instruct user" applies.
    # We will try to rely on existing server or fail gracefully.

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock the API calls to ensure consistent game state
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"output": "SYSTEM ONLINE.", "state": {"sanity": 50, "reality": 50, "location": "HQ", "time": "08:00", "day": "14"}}'
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=30000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            print("Make sure the dev server is running (pnpm dev).")
            browser.close()
            sys.exit(1)

        print("Page loaded.")

        # Click Start Investigation
        start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
        try:
            start_btn.wait_for(timeout=10000)
            start_btn.click()
            print("Clicked start button.")
        except:
            print("Start button not found.")
            browser.close()
            sys.exit(1)

        # Wait for VHSEffect container
        vhs_container = page.locator(".vhs-container")
        try:
            vhs_container.wait_for(timeout=10000)
            print("VHSEffect container found.")
        except:
            print("VHSEffect container not found.")
            browser.close()
            sys.exit(1)

        # Elements to monitor
        glitch_overlay = page.locator(".glitch-overlay")
        static_noise = page.locator(".static-noise")
        tape_counter = page.locator(".tape-counter")

        # Sampling Loop
        samples = []
        print("Sampling visual styles...")
        for i in range(5):
            # Get current styles
            transform = glitch_overlay.evaluate("el => el.style.transform")
            opacity = static_noise.evaluate("el => el.style.opacity")
            counter_text = tape_counter.inner_text()

            samples.append({
                "transform": transform,
                "opacity": opacity,
                "counter": counter_text
            })

            time.sleep(0.1) # Wait 100ms

        # Verify changes
        transforms = [s["transform"] for s in samples]
        opacities = [s["opacity"] for s in samples]
        counters = [s["counter"] for s in samples]

        print("Transforms sampled:", transforms)
        print("Opacities sampled:", opacities)
        print("Counters sampled:", counters)

        # Check if values are changing (at least some uniqueness)
        unique_transforms = set(transforms)
        unique_opacities = set(opacities)
        unique_counters = set(counters)

        if len(unique_transforms) <= 1:
            print("FAIL: Glitch overlay transform is not changing!")
            browser.close()
            sys.exit(1)

        if len(unique_opacities) <= 1:
            print("FAIL: Static noise opacity is not changing!")
            browser.close()
            sys.exit(1)

        if len(unique_counters) <= 1:
            print("FAIL: Tape counter is not changing!")
            browser.close()
            sys.exit(1)

        print("SUCCESS: Visual effects are animating.")

        # Take a screenshot for visual verification
        page.screenshot(path="verification/vhs_optimized.png")
        print("Screenshot saved to verification/vhs_optimized.png")

        browser.close()

if __name__ == "__main__":
    run()
