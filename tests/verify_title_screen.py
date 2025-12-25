import os
import sys
from playwright.sync_api import sync_playwright

def verify_title_screen():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Construct absolute file path
        cwd = os.getcwd()
        file_path = os.path.join(cwd, "title_screen", "index.html")
        url = f"file://{file_path}"

        print(f"Loading: {url}")
        page.goto(url)

        # Wait for fonts and animations to settle
        page.wait_for_timeout(2000)

        # Verify elements exist
        title = page.locator(".main-title-glitch")
        menu = page.locator(".main-menu")
        crt = page.locator(".crt-screen-container")

        if title.count() > 0 and menu.count() > 0 and crt.count() > 0:
            print("SUCCESS: Key elements found.")
        else:
            print("FAILURE: Key elements missing.")
            sys.exit(1)

        # Take screenshot for visual inspection
        output_dir = os.path.join(cwd, "tests", "artifacts")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, "title_screen_verify.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_title_screen()
