from playwright.sync_api import sync_playwright, expect
import os

def verify_title_screen_ux():
    os.makedirs("verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to http://localhost:5173")
        page.goto("http://localhost:5173")

        # Wait for title screen to load (animations take time)
        # The title screen has initial animations of ~2.5s
        page.wait_for_timeout(4000)

        # 1. Verify ARIA Labels
        print("Verifying ARIA labels...")
        start_btn = page.get_by_label("Start Investigation")
        exit_btn = page.get_by_label("Exit System")

        expect(start_btn).to_be_visible()
        print("✅ 'Start Investigation' button found via ARIA label")

        expect(exit_btn).to_be_visible()
        print("✅ 'Exit System' button found via ARIA label")

        # 2. Verify Focus Styles
        print("Verifying focus styles...")
        # Focus the start button
        start_btn.focus()
        page.wait_for_timeout(500) # Wait for transition

        # Take a screenshot of the focused state
        screenshot_path = "verification/titlescreen_focused.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot taken: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_title_screen_ux()
