from playwright.sync_api import sync_playwright, expect
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock the API calls so we don't need the backend
        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"output": "SYSTEM ONLINE.", "state": {"sanity": 80, "reality": 60, "location": "HQ", "time": "08:00", "day": "14", "mental_load": 50, "attention_level": 50}}'
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=60000)
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
             print("Start button not found or verify failed.")
             page.screenshot(path="verification/debug_vhs_fail_start.png")
             browser.close()
             return

        # Wait for VHS effect to be active
        # The .glitch-overlay should exist
        glitch_overlay = page.locator(".glitch-overlay")
        try:
            glitch_overlay.wait_for(state="attached", timeout=10000)
        except:
             print("VHS Glitch Overlay not found.")
             page.screenshot(path="verification/debug_vhs_fail_overlay.png")
             browser.close()
             return

        print("VHS Overlay found. Checking for animation updates...")

        # Get initial transform
        initial_transform = glitch_overlay.get_attribute("style")
        print(f"Initial style: {initial_transform}")

        # Wait a bit (approx 200ms)
        time.sleep(0.2)

        # Get transform again
        second_transform = glitch_overlay.get_attribute("style")
        print(f"Second style: {second_transform}")

        if initial_transform == second_transform:
            print("FAIL: Style did not update. Animation loop might be broken.")
            # It's possible random chance made it same, so try one more time
            time.sleep(0.2)
            third_transform = glitch_overlay.get_attribute("style")
            print(f"Third style: {third_transform}")
            if second_transform == third_transform:
                 print("FAIL: Style still did not update.")
                 # Fail but take screenshot
            else:
                 print("PASS: Style updated on second try.")
        else:
            print("PASS: Style updated.")

        # Check Tape Counter
        counter = page.locator(".tape-counter")
        if counter.count() > 0:
            text = counter.inner_text()
            print(f"Tape Counter Text: {text}")
            if "SP 0:00:" in text:
                print("PASS: Tape counter format correct.")
            else:
                print("FAIL: Tape counter format incorrect.")
        else:
            print("FAIL: Tape counter not found.")

        # Take screenshot
        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/vhs_render.png")
        print("Screenshot saved to verification/vhs_render.png")

        browser.close()

if __name__ == "__main__":
    run()
