from playwright.sync_api import sync_playwright, expect
import time
import os

def verify_title_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Navigating to app...")
            page.goto("http://localhost:5173")

            # Wait for title animation (approx 3s)
            time.sleep(3)

            # Check Start Button
            print("Checking Start Button...")
            start_btn = page.locator("button.start-btn")
            expect(start_btn).to_be_visible()

            aria_label = start_btn.get_attribute("aria-label")
            print(f"Start Button aria-label: {aria_label}")

            if aria_label == "Start Investigation":
                print("SUCCESS: Start button has correct ARIA label.")
            else:
                print("INFO: Start button does NOT have correct ARIA label yet.")

            # Check Exit Button
            print("Checking Exit Button...")
            exit_btn = page.locator("button.exit-btn")
            expect(exit_btn).to_be_visible()

            aria_label_exit = exit_btn.get_attribute("aria-label")
            print(f"Exit Button aria-label: {aria_label_exit}")

            if aria_label_exit == "Exit System":
                print("SUCCESS: Exit button has correct ARIA label.")
            else:
                print("INFO: Exit button does NOT have correct ARIA label yet.")

            # Check Focus Styles (Visual verification via screenshot)
            print("Testing Keyboard Focus...")
            page.keyboard.press("Tab") # Focus Start Button
            time.sleep(0.5)

            # Take screenshot of focused start button
            os.makedirs("verification", exist_ok=True)
            page.screenshot(path="verification/title_focus_start.png")
            print("Screenshot saved: verification/title_focus_start.png")

            page.keyboard.press("Tab") # Focus Exit Button
            time.sleep(0.5)
            page.screenshot(path="verification/title_focus_exit.png")
            print("Screenshot saved: verification/title_focus_exit.png")

        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_title_ux()
