import time
from playwright.sync_api import sync_playwright

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            print("Navigating to frontend...")
            page.goto("http://localhost:5173", timeout=30000)

            # Click start button on title screen
            print("Waiting for start button...")
            page.get_by_text("[START_INVESTIGATION]").click()

            # Wait for the terminal (after boot sequence)
            # Boot sequence is ~4.4s, so we wait enough time
            print("Waiting for boot sequence and terminal...")
            page.wait_for_selector(".terminal-window", timeout=15000)

            # Wait a bit more for text to appear
            time.sleep(2)

            # Take a screenshot
            screenshot_path = "verification/terminal_verification.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Verification failed: {e}")
            try:
                page.screenshot(path="verification/failure.png")
            except:
                pass
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
