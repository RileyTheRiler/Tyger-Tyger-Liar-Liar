from playwright.sync_api import sync_playwright, expect
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Debug logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

        print("Navigating to app...")
        try:
            page.goto("http://localhost:5173", timeout=10000)

            print("Waiting for start button...")
            start_btn = page.get_by_text("[START_INVESTIGATION]")
            expect(start_btn).to_be_visible(timeout=10000)

            page.screenshot(path="verification/1_title_screen.png")
            print("Title screen captured.")

            print("Starting investigation...")
            start_btn.click()

            print("Waiting for terminal...")
            page.wait_for_selector(".terminal-window", timeout=15000)

            time.sleep(2)

            expect(page.locator(".terminal-content")).to_be_visible()

            page.screenshot(path="verification/2_terminal_active.png")
            print("Terminal captured.")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_state.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_frontend()
