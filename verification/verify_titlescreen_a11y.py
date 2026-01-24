from playwright.sync_api import sync_playwright, expect
import os
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the app (assuming it's running on localhost:5173 from previous step)
        url = "http://localhost:5173"
        print(f"Navigating to {url}")
        try:
            page.goto(url, timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            sys.exit(1)

        # Wait for Title Screen buttons
        start_btn = page.locator("button.start-btn")
        exit_btn = page.locator("button.exit-btn")

        print("Waiting for buttons...")
        try:
            start_btn.wait_for(timeout=5000)
            exit_btn.wait_for(timeout=5000)
        except Exception as e:
            print(f"Buttons not found: {e}")
            page.screenshot(path="verification/titlescreen_fail.png")
            sys.exit(1)

        # Verify aria-labels
        print("Verifying ARIA labels...")

        start_label = start_btn.get_attribute("aria-label")
        if start_label == "Start Investigation":
            print("SUCCESS: Start button has correct aria-label")
        else:
            print(f"FAILURE: Start button aria-label is '{start_label}'")
            sys.exit(1)

        exit_label = exit_btn.get_attribute("aria-label")
        if exit_label == "Exit System":
            print("SUCCESS: Exit button has correct aria-label")
        else:
            print(f"FAILURE: Exit button aria-label is '{exit_label}'")
            sys.exit(1)

        # Verify aria-hidden on inner span
        print("Verifying aria-hidden on inner text...")
        start_span = start_btn.locator("span")
        if start_span.get_attribute("aria-hidden") == "true":
             print("SUCCESS: Start button text is hidden from screen reader")
        else:
             print("FAILURE: Start button span missing aria-hidden='true'")
             sys.exit(1)

        # Verify Focus Styles
        print("Testing focus styles...")
        # Focus the start button
        start_btn.focus()

        # Take a screenshot
        os.makedirs("verification", exist_ok=True)
        screenshot_path = "verification/titlescreen_focus.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Verify focus
        is_focused = page.evaluate("document.activeElement === document.querySelector('.start-btn')")
        if is_focused:
            print("SUCCESS: Start button is focused")
        else:
            print("FAILURE: Start button did not receive focus")

        browser.close()

if __name__ == "__main__":
    run()
