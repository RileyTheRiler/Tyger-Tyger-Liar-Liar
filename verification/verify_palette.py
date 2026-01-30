from playwright.sync_api import sync_playwright, expect
import time
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to http://localhost:5173...")
            page.goto("http://localhost:5173")

            # Wait for title screen content
            try:
                page.wait_for_selector(".title-screen", state="visible", timeout=5000)
            except:
                print("Title screen not found, dumping content...")
                print(page.content())
                raise

            # Verify TitleScreen buttons
            start_btn = page.locator(".start-btn")
            exit_btn = page.locator(".exit-btn")

            start_label = start_btn.get_attribute("aria-label")
            exit_label = exit_btn.get_attribute("aria-label")

            print(f"Start Button Label: '{start_label}'")
            print(f"Exit Button Label: '{exit_label}'")

            if start_label != "Start Investigation":
                raise Exception(f"Expected 'Start Investigation', got '{start_label}'")
            if exit_label != "Exit System":
                raise Exception(f"Expected 'Exit System', got '{exit_label}'")

            # Verify GlitchText in TitleScreen
            title_main = page.locator(".title-main")
            title_label = title_main.get_attribute("aria-label")
            print(f"Title Main Label: '{title_label}'")

            if title_label != "TYGER TYGER":
                raise Exception(f"Expected 'TYGER TYGER', got '{title_label}'")

            # Take screenshot
            page.screenshot(path="verification/palette_title_screen.png")
            print("Verification SUCCESS")

        except Exception as e:
            print(f"Verification FAILED: {e}")
            page.screenshot(path="verification/failure.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
